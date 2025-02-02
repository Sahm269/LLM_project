import os
from mistralai import Mistral
import chromadb
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd

# class MistralAPI:
#     """
#     A client for interacting with the MistralAI API.

#     Attributes:
#         client (Mistral): The Mistral client instance.
#         model (str): The model to use for queries.
#     """

#     def __init__(self, model: str) -> None:
#         """
#         Initializes the MistralAPI with the given model.

#         Args:
#             model (str): The model to use for queries.

#         Raises:
#             ValueError: If the MISTRAL_API_KEY environment variable is not set.
#         """
#         api_key = os.getenv("MISTRAL_API_KEY")
#         if not api_key:
#             raise ValueError(
#                 "No MISTRAL_API_KEY as environment variable, please set it!"
#             )
#         self.client = Mistral(api_key=api_key)
#         self.model = model


#     def auto_wrap(self, text: str, temperature: float = 0.5) -> str:
#         """
#         Sends a query to the MistralAI API and returns the response.

#         Args:
#             query (str): The input query to send to the model.
#             temperature (float, optional): The temperature parameter for controlling
#                                           the randomness of the output. Defaults to 0.5.

#         Returns:
#             str: The response from the API.
#         """
#         chat_response = self.client.chat.complete(
#             model=self.model,
#             temperature=temperature,
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "Résume le sujet de l'instruction ou de la question suivante en quelques mots. Ta réponse doit faire 30 caractères au maximum.",
#                 },
#                 {
#                     "role": "user",
#                     "content": text,
#                 },
#             ]
#         )
#         return chat_response.choices[0].message.content


#     def stream(self, messages: str, temperature: float = 0.5) -> str:
#         """
#         Sends a query to the MistralAI API and returns the response.

#         Args:
#             query (str): The input query to send to the model.
#             temperature (float, optional): The temperature parameter for controlling
#                                           the randomness of the output. Defaults to 0.5.

#         Returns:
#             str: The response from the API.
#         """
#         chat_response = self.client.chat.stream(
#             model=self.model,
#             temperature=temperature,
#             messages=[
#                 {"role": "system",
#                     "content": """
#                     Tu es un expert en nutrition et en alimentation saine. Ta mission est de fournir des recommandations personnalisées, équilibrées et adaptées aux objectifs de santé et de bien-être des utilisateurs. Lorsque tu réponds, veille à respecter les points suivants :

#                     Clarté et précision : Tes réponses doivent être claires, concises et faciles à comprendre.
#                     Équilibre alimentaire : Propose des solutions respectant une alimentation équilibrée (protéines, glucides, lipides, vitamines, minéraux).
#                     Adaptabilité : Adapte tes suggestions en fonction des préférences alimentaires (ex. : végétarien, végan, sans gluten, faible en glucides, etc.), des allergies, ou des restrictions médicales éventuelles.
#                     Objectifs de santé : Prends en compte les objectifs spécifiques de l'utilisateur (ex. : perte de poids, prise de masse musculaire, énergie durable, meilleure digestion).
#                     Simples et accessibles : Propose des recettes ou des aliments faciles à préparer ou à trouver, en privilégiant des ingrédients frais et naturels.
#                     Conseils bienveillants : Fournis des recommandations qui encouragent de bonnes habitudes alimentaires, sans culpabilisation.
#                     Exemple de Structure de Réponse :
#                     Suggestion principale :

#                     Exemple : "Pour un déjeuner sain et équilibré, essayez une salade de quinoa avec des légumes grillés, des pois chiches et une vinaigrette au citron et à l'huile d'olive."
#                     Valeur nutritionnelle :

#                     Exemple : "Ce repas est riche en fibres, en protéines végétales, et en vitamines A et C, tout en étant faible en graisses saturées."
#                     Adaptation possible :

#                     Exemple : "Si vous suivez un régime pauvre en glucides, remplacez le quinoa par des courgettes en spirale (zoodles)."
#                     Astuces ou options supplémentaires :

#                     Exemple : "Ajoutez des graines de chia ou de lin pour un apport supplémentaire en oméga-3."
#                     Rôle de Langue :
#                     Utilise un ton amical, motivant, et professionnel tout en restant empathique pour accompagner l’utilisateur dans ses choix alimentaires sains.
#                     """
#                     }]+[
#                 {"role": m["role"], "content": m["content"]}
#                 for m in messages
#             ]
#         )
#         return chat_response


class MistralAPI:
    """
    A client for interacting with the MistralAI API with RAG (Retrieval-Augmented Generation).
    """

    # Stockage du modèle d'embedding en variable de classe pour éviter de le recharger plusieurs fois
    embedding_model = None

    def __init__(self, model: str) -> None:
        """
        Initializes the MistralAPI with the given model and sets up ChromaDB for RAG.
        """
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("No MISTRAL_API_KEY found. Please set it in environment variables!")
        self.client = Mistral(api_key=api_key)
        self.model = model

        # Charger le modèle d'embedding une seule fois
        if MistralAPI.embedding_model is None:
            print("🔄 Chargement du modèle d'embedding...")
            MistralAPI.embedding_model = SentenceTransformer(
                'dangvantuan/french-document-embedding', trust_remote_code=True
            )
            print("✅ Modèle d'embedding chargé avec succès.")
        else:
            print("✅ Modèle d'embedding déjà chargé, pas de rechargement nécessaire.")

        # Charger les données et les embeddings
        self.load_data()

        # Initialiser ChromaDB (avec persistance)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="recettes")

        # Vérifier si ChromaDB contient déjà des recettes
        nb_recettes = self.collection.count()
        print(f"📊 Nombre de recettes actuellement dans ChromaDB : {nb_recettes}")

        # Ajouter les données à ChromaDB si la collection est vide
        if nb_recettes == 0:
            self.populate_chromadb()
        else:
            print("✅ ChromaDB contient déjà des recettes, pas d'ajout nécessaire.")

    def load_data(self):
        """Charge les fichiers de recettes et d'embeddings"""
        data_path = "./server/data/cleaned_data.parquet"
        embeddings_path = "./server/data/embeddings.pkl"

        if not os.path.exists(data_path) or not os.path.exists(embeddings_path):
            raise FileNotFoundError("❌ Les fichiers de données ou d'embeddings sont introuvables !")

        # Charger les données clean
        self.df = pd.read_parquet(data_path)

        # Charger les embeddings des recettes
        with open(embeddings_path, "rb") as f:
            self.embeddings = pickle.load(f)

        print(f"✅ {len(self.df)} recettes chargées avec succès.")

    def populate_chromadb(self):
        """Ajoute les recettes et embeddings dans ChromaDB"""
        print("🔄 Ajout des recettes dans ChromaDB...")
        for i, (embedding, row) in enumerate(zip(self.embeddings, self.df.iterrows())):
            _, row_data = row
            self.collection.add(
                ids=[str(i)],  # ID unique
                embeddings=[embedding.tolist()],  # Embedding sous forme de liste
                metadatas=[{
                    "Titre": row_data["Titre"],
                    "Temps de préparation": row_data["Temps de préparation"],
                    "Ingrédients": row_data["Ingrédients"],
                    "Instructions": row_data["Instructions"],
                    "Infos régime": row_data["Infos régime"],
                    "Valeurs pour 100g": row_data["Valeurs pour 100g"],
                    "Valeurs par portion": row_data["Valeurs par portion"]
                }]
            )
        print(f"✅ {self.collection.count()} recettes ajoutées dans ChromaDB.")

    def search_recipe(self, query: str, top_k: int = 3) -> list:
        """
        Recherche les recettes les plus pertinentes dans ChromaDB en fonction de la requête utilisateur.
        """
        query_embedding = MistralAPI.embedding_model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        if not results["ids"][0]:
            return []

        recipes = []
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            recipes.append(metadata)

        return recipes

    def get_contextual_response(self, messages: list, temperature: float = 0.5) -> str:
        """
        Récupère une réponse contextuelle en intégrant les données de ChromaDB si l'utilisateur demande une recette.
        """
        query = messages[-1]["content"]  # Récupérer la dernière question de l'utilisateur
        recipes = self.search_recipe(query, top_k=3)

        if recipes:  # Si on trouve des recettes, les afficher
            context = "Voici des recettes similaires trouvées dans ma base :\n\n"
            for recipe in recipes:
                context += f"""**Nom :** {recipe['Titre']}
                **Temps de préparation :** {recipe['Temps de préparation']}
                **Ingrédients :** {recipe['Ingrédients']}
                **Instructions :** {recipe['Instructions']}
                **Valeurs nutritionnelles (100g) :** {recipe['Valeurs pour 100g']}
                **Valeurs nutritionnelles (par portion) :** {recipe['Valeurs par portion']}\n\n"""
        else:  # Si aucune recette trouvée, laisser Mistral improviser
            context = "Je n’ai pas trouvé de recette exacte en base, mais voici une idée basée sur ton besoin :"

        # Injecter le contexte + instructions précises pour Mistral
        enriched_messages = [
            {"role": "system", "content": """
                Tu es un expert en nutrition et en alimentation saine. Ta mission est de fournir des recommandations personnalisées, équilibrées et adaptées aux objectifs de santé et de bien-être des utilisateurs. Lorsque tu réponds, veille à respecter les points suivants :

                Clarté et précision : Tes réponses doivent être claires, concises et faciles à comprendre.
                Équilibre alimentaire : Propose des solutions respectant une alimentation équilibrée (protéines, glucides, lipides, vitamines, minéraux).
                Adaptabilité : Adapte tes suggestions en fonction des préférences alimentaires (ex. : végétarien, végan, sans gluten, faible en glucides, etc.), des allergies, ou des restrictions médicales éventuelles.
                Objectifs de santé : Prends en compte les objectifs spécifiques de l'utilisateur (ex. : perte de poids, prise de masse musculaire, énergie durable, meilleure digestion).
                Simples et accessibles : Propose des recettes ou des aliments faciles à préparer ou à trouver, en privilégiant des ingrédients frais et naturels.
                Conseils bienveillants : Fournis des recommandations qui encouragent de bonnes habitudes alimentaires, sans culpabilisation.
            """},
            {"role": "assistant", "content": context}
        ] + messages

        # Générer une réponse avec Mistral
        chat_response = self.client.chat.stream(
            model=self.model,
            temperature=temperature,
            messages=enriched_messages
        )

        return chat_response

    def stream(self, messages: list, temperature: float = 0.5) -> str:
        """
        Enrichit la réponse avec la RAG avant d'envoyer à Mistral.
        """
        return self.get_contextual_response(messages, temperature)
    
    def auto_wrap(self, text: str, temperature: float = 0.5) -> str:
        """
        Génère un titre court basé sur la requête utilisateur.
        """
        chat_response = self.client.chat.complete(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": "Résume le sujet de l'instruction ou de la question suivante en quelques mots. "
                            "Ta réponse doit faire 30 caractères au maximum.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ]
        )
        return chat_response.choices[0].message.content


