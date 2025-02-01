import os
from mistralai import Mistral


class MistralAPI:
    """
    A client for interacting with the MistralAI API.

    Attributes:
        client (Mistral): The Mistral client instance.
        model (str): The model to use for queries.
    """

    def __init__(self, model: str) -> None:
        """
        Initializes the MistralAPI with the given model.

        Args:
            model (str): The model to use for queries.

        Raises:
            ValueError: If the MISTRAL_API_KEY environment variable is not set.
        """
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "No MISTRAL_API_KEY as environment variable, please set it!"
            )
        self.client = Mistral(api_key=api_key)
        self.model = model


    def auto_wrap(self, text: str, temperature: float = 0.5) -> str:
        """
        Sends a query to the MistralAI API and returns the response.

        Args:
            query (str): The input query to send to the model.
            temperature (float, optional): The temperature parameter for controlling
                                          the randomness of the output. Defaults to 0.5.

        Returns:
            str: The response from the API.
        """
        chat_response = self.client.chat.complete(
            model=self.model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": "Résume le sujet de l'instruction ou de la question suivante en quelques mots. Ta réponse doit faire 30 caractères au maximum.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ]
        )
        return chat_response.choices[0].message.content


    def stream(self, messages: str, temperature: float = 0.5) -> str:
        """
        Sends a query to the MistralAI API and returns the response.

        Args:
            query (str): The input query to send to the model.
            temperature (float, optional): The temperature parameter for controlling
                                          the randomness of the output. Defaults to 0.5.

        Returns:
            str: The response from the API.
        """
        chat_response = self.client.chat.stream(
            model=self.model,
            temperature=temperature,
            messages=[
                {"role": "system",
                    "content": """
                    Tu es un expert en nutrition et en alimentation saine. Ta mission est de fournir des recommandations personnalisées, équilibrées et adaptées aux objectifs de santé et de bien-être des utilisateurs. Lorsque tu réponds, veille à respecter les points suivants :

                    Clarté et précision : Tes réponses doivent être claires, concises et faciles à comprendre.
                    Équilibre alimentaire : Propose des solutions respectant une alimentation équilibrée (protéines, glucides, lipides, vitamines, minéraux).
                    Adaptabilité : Adapte tes suggestions en fonction des préférences alimentaires (ex. : végétarien, végan, sans gluten, faible en glucides, etc.), des allergies, ou des restrictions médicales éventuelles.
                    Objectifs de santé : Prends en compte les objectifs spécifiques de l'utilisateur (ex. : perte de poids, prise de masse musculaire, énergie durable, meilleure digestion).
                    Simples et accessibles : Propose des recettes ou des aliments faciles à préparer ou à trouver, en privilégiant des ingrédients frais et naturels.
                    Conseils bienveillants : Fournis des recommandations qui encouragent de bonnes habitudes alimentaires, sans culpabilisation.
                    Exemple de Structure de Réponse :
                    Suggestion principale :

                    Exemple : "Pour un déjeuner sain et équilibré, essayez une salade de quinoa avec des légumes grillés, des pois chiches et une vinaigrette au citron et à l'huile d'olive."
                    Valeur nutritionnelle :

                    Exemple : "Ce repas est riche en fibres, en protéines végétales, et en vitamines A et C, tout en étant faible en graisses saturées."
                    Adaptation possible :

                    Exemple : "Si vous suivez un régime pauvre en glucides, remplacez le quinoa par des courgettes en spirale (zoodles)."
                    Astuces ou options supplémentaires :

                    Exemple : "Ajoutez des graines de chia ou de lin pour un apport supplémentaire en oméga-3."
                    Rôle de Langue :
                    Utilise un ton amical, motivant, et professionnel tout en restant empathique pour accompagner l’utilisateur dans ses choix alimentaires sains.
                    """
                    }]+[
                {"role": m["role"], "content": m["content"]}
                for m in messages
            ]
        )
        return chat_response