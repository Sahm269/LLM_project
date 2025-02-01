import streamlit as st
import os
from datetime import datetime
import time
from mistralai import Mistral
import numpy as np
from mistralai.models.sdkerror import SDKError
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("api_key")
mistral_client = Mistral(api_key=api_key)

st.markdown(
    """
    <style>
        .title-container {
            background-color: #6A5ACD;
            border-radius: 10px;
            color: white;
            text-align: center;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            font-family: New Icon;
            font-size: 25px;
        }

       
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-container">
        CHATBOT
    </div>
    """,
    unsafe_allow_html=True,
)



db_manager = st.session_state["db_manager"]
user_id = st.session_state["user_id"]



def save_message(db_manager, id_conversation: int, role: str, content: str) -> None:
    """
    Sauvegarde un message dans la base de données, en associant l'utilisateur à la conversation.
    
    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation associée.
    :param role: Rôle de l'intervenant (ex. 'user' ou 'assistant').
    :param content: Contenu du message.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [{
        "id_conversation": id_conversation,
        "role": role,
        "content": content,
        "timestamp": timestamp,
      
    }]
    db_manager.insert_data_from_dict("messages", data, id_column="id_message")



def create_conversation(db_manager, title: str, id_utilisateur: int) -> int:
    """
    Crée une nouvelle conversation dans la base de données, en associant l'utilisateur à la conversation.
    
    :param db_manager: Instance de DBManager.
    :param title: Titre de la conversation.
    :param id_utilisateur: ID de l'utilisateur associé.
    :return: ID de la conversation nouvellement créée.
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [{
        "created_at": created_at,
        "title": title,
        "id_utilisateur": id_utilisateur,
      
    }]
    result = db_manager.insert_data_from_dict("conversations", data, id_column="id_conversation")



   
    return result[0]


def load_messages(db_manager, id_conversation: int) -> List[Dict]:
    """
    Charge les messages associés à une conversation.
    
    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation.
    :return: Liste des messages sous forme de dictionnaires.
    """
    query = """
        SELECT role, content 
        FROM messages 
        WHERE id_conversation = %s 
        ORDER BY timestamp ASC
    """
    result = db_manager.query(query, (id_conversation,))
    return [{"role": row[0], "content": row[1]} for row in result]


def load_conversations(db_manager, id_utilisateur: int) -> List[Dict]:
    """
    Charge toutes les conversations enregistrées pour un utilisateur donné.
    
    :param db_manager: Instance de DBManager.
    :param id_utilisateur: ID de l'utilisateur.
    :return: Liste des conversations.
    """
    query = """
        SELECT * FROM conversations 
        WHERE id_utilisateur = %s
        ORDER BY created_at DESC
    """
    result = db_manager.query(query, (id_utilisateur,))
    return [
        {"id_conversation": row[0], "created_at": row[1], "title": row[2]} for row in result
    ]


def update_conversation(db_manager, id_conversation: int, id_utilisateur: int) -> None:
    """
    Met à jour le champ `created_at` d'une conversation donnée pour un utilisateur.
    
    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation à mettre à jour.
    :param id_utilisateur: ID de l'utilisateur.
    """
    new_timer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = """
        UPDATE conversations 
        SET created_at = %s 
        WHERE id_conversation = %s AND id_utilisateur = %s
    """
    db_manager.query(query, (new_timer, id_conversation, id_utilisateur))


def update_conversation_title(db_manager, id_conversation: int, new_title: str) -> None:
    """
    Met à jour le titre d'une conversation si celui-ci est encore "Nouvelle conversation".

    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation à mettre à jour.
    :param new_title: Nouveau titre de la conversation.
    """
    query = """
        UPDATE conversations 
        SET title = %s
        WHERE id_conversation = %s AND title = 'Nouvelle conversation'
    """
    db_manager.query(query, (new_title, id_conversation))



def get_conversation_title(db_manager, id_conversation: int) -> str:
    """
    Récupère le titre d'une conversation spécifique en utilisant `fetch_by_condition`.

    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation à interroger.
    :return: Le titre de la conversation ou "Nouvelle conversation".
    """
    table_name = "conversations"
    condition = "id_conversation = %s"
    results = db_manager.fetch_by_condition(table_name, condition, (id_conversation,))

    if results:
        # Suppose que `title` est la troisième colonne
        return results[0][2]
    return "Nouvelle conversation"






def get_title(text, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            # Tentative d'appel à l'API Mistral
            chat_response = mistral_client.chat.complete(
                model=st.session_state["mistral_model"],
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
            # Retourner le résultat si l'appel réussit
            return chat_response.choices[0].message.content
        except Exception as e:
            # Vérifier explicitement si l'erreur est une 429 (rate limit exceeded)
            if hasattr(e, "status_code") and e.status_code == 429:
                retries += 1
                wait_time = 2 ** retries  # Temps d'attente exponentiel
                st.warning(f"Limite de requêtes atteinte (429). Nouvel essai dans {wait_time} secondes...")
                time.sleep(wait_time)
            else:
                # Gérer d'autres types d'erreurs
                st.error(f"Erreur inattendue : {str(e)}")
                return "Erreur : Impossible de traiter votre demande."
    # Si tous les retries échouent, retourner un message d'erreur
    st.error("Impossible d'obtenir une réponse après plusieurs tentatives.")
    return "Erreur : Limite de requêtes atteinte après plusieurs tentatives."





# Section pour afficher l'historique de la conversation
conversation_history = load_conversations(db_manager,user_id)

st.sidebar.title("Historique")
for index, conversation in enumerate(conversation_history):
    id_conversation = conversation['id_conversation']
    title = conversation['title']
    key = f"conversation_{id_conversation}_{index}"  # Clé unique pour chaque bouton
    
    # Vérifier si cette conversation est active
    if "id_conversation" in st.session_state and st.session_state.id_conversation == id_conversation:
        # Bouton désactivé pour la conversation active
        st.sidebar.button(f"🟢 {title}", key=key, disabled=True)
    else:
        # Bouton actif pour sélectionner une autre conversation
        if st.sidebar.button(title, key=key):
            # Charger la conversation sélectionnée
            st.session_state.id_conversation = id_conversation
            st.session_state.messages = load_messages(db_manager, id_conversation)
            update_conversation(db_manager,id_conversation=st.session_state.id_conversation,id_utilisateur=user_id)
            st.rerun()
            
# Ajouter un bouton pour démarrer une nouvelle conversation
if st.sidebar.button("➕ Nouveau chat"):
    # Créer une nouvelle conversation
    title = "Nouvelle conversation"
    new_conversation_id = create_conversation(db_manager, title, user_id)

    # Initialiser la session avec cette nouvelle conversation
    st.session_state.id_conversation = new_conversation_id
    st.session_state.messages = []  # Réinitialiser les messages

    # Redémarrer l'application pour afficher la nouvelle conversation
    st.rerun()


# Historique de la conversation
if "id_conversation" not in st.session_state:
    st.session_state.id_conversation = None

# Affichage des messages précédents
if st.session_state.id_conversation:
    st.session_state.messages = load_messages(db_manager,st.session_state.id_conversation)

if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = "mistral-large-latest"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):  # Utilisez votre avatar utilisateur
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="avatar_bot.jpg"):  # Avatar personnalisé pour l'assistant
            st.markdown(message["content"])

if prompt := st.chat_input("Dîtes quelque-chose"):
    if st.session_state.id_conversation is None:
        # Générer un titre basé sur le premier message
        title = get_title(text=prompt)
        st.session_state.id_conversation = create_conversation(db_manager, title, user_id)
    else:
        # Vérifier si le titre est encore "Nouvelle conversation" et le mettre à jour si nécessaire
        current_title = get_conversation_title(db_manager, st.session_state.id_conversation)
        if current_title == "Nouvelle conversation":
            new_title = get_title(text=prompt)
            update_conversation_title(db_manager, st.session_state.id_conversation, new_title)

    # Ajouter le message de l'utilisateur à la session et à la base de données
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(db_manager=db_manager, id_conversation=st.session_state.id_conversation, role="user", content=prompt)

    # Afficher le message de l'utilisateur dans l'interface Streamlit
    with st.chat_message("user"):
        st.markdown(prompt)


    with st.chat_message("assistant", avatar = "avatar_bot.jpg"):
        retries = 0
        max_retries = 3
        while retries < max_retries:
            try:
                # Tentative d'appel à l'API Mistral
                stream_response = mistral_client.chat.stream(
                    model=st.session_state["mistral_model"],
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
                        for m in st.session_state.messages
                    ]
                )
                response = ""
                response_placeholder = st.empty()
                # Traiter la réponse en streaming
                for chunk in stream_response:
                    response += chunk.data.choices[0].delta.content
                    response_placeholder.markdown(response)
                    time.sleep(0.03)  # Petit délai pour simuler le flux en temps réel
                break  # Si le streaming réussit, on sort de la boucle
            except Exception as e:
                if hasattr(e, "status_code") and e.status_code == 429:
                    # Gestion explicite de l'erreur 429 (Rate Limit Exceeded)
                    retries += 1
                    wait_time = 2 ** retries  # Délai exponentiel : 2, 4, 8 secondes
                    st.warning(f"Limite de requêtes atteinte (429). Nouvel essai dans {wait_time} secondes...")
                    time.sleep(wait_time)
                else:
                    # Gestion d'autres types d'erreurs
                    st.error(f"Une erreur est survenue : {str(e)}")
                    response_placeholder.markdown("Erreur lors de la génération de la réponse.")
                    break
        # Si toutes les tentatives échouent, message d'erreur final
        if retries == max_retries:
            st.error("Impossible d'obtenir une réponse après plusieurs tentatives.")
            response = "Erreur : Limite de requêtes atteinte après plusieurs tentatives."
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message(db_manager,id_conversation=st.session_state.id_conversation, role="assistant", content=response)





