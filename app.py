import streamlit as st
import sqlite3
from mistralai import Mistral
from datetime import datetime
import time
import numpy as np
from mistralai.models.sdkerror import SDKError
from security.input_validation import Guardrail


# Configuration de la base de données SQLite
DB_NAME = "chat_history.db"
# Initialisation du client Mistral
api_key = "RXjfbTO7wkOU0RwrwP7XpFfcj1K5eq40"
mistral_client = Mistral(api_key=api_key)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            title TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_message(conversation_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.execute("INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
              (conversation_id, role, content, timestamp))
    conn.commit()
    conn.close()

def create_conversation(title):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO conversations (created_at, title) VALUES (?, ?)", (created_at, title))
    conversation_id = c.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def load_messages(conversation_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation_id,))
    data = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return data

def load_conversations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM conversations ORDER BY created_at DESC") 
    data = c.fetchall()
    conn.close()
    return data

def update_conversation(conversation_id):
    conn = sqlite3.connect(DB_NAME)
    new_timer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c = conn.cursor()
    c.execute("UPDATE conversations SET created_at = ? WHERE id = ?",(new_timer, conversation_id))
    conn.commit()
    conn.close()

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

# Initialisation de la base de données
init_db()

# Interface Streamlit
st.set_page_config(page_title="Nutrigénie", layout="wide")
# Section pour afficher l'historique de la conversation
conversation_history = load_conversations()
st.sidebar.title("Navigation")
st.sidebar.title("Historique")

for conversation_id, _, title in conversation_history:
    if "conversation_id" in st.session_state and st.session_state.conversation_id == conversation_id:
        # Bouton désactivé pour la conversation active
        st.sidebar.button(f"🟢 {title}", key=f"conversation_{conversation_id}", disabled=True)
    else:
        # Bouton actif pour les autres conversations
        if st.sidebar.button(title, key=f"conversation_{conversation_id}"):
            # Charger la conversation sélectionnée
            st.session_state.conversation_id = conversation_id
            st.session_state.messages = load_messages(conversation_id)
            update_conversation(conversation_id=st.session_state.conversation_id)
            st.rerun()

st.title("Parlez au Nutrigénie")
# Historique de la conversation
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Affichage des messages précédents
if st.session_state.conversation_id:
    st.session_state.messages = load_messages(st.session_state.conversation_id)

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
    if st.session_state.conversation_id is None:
        title = get_title(text=prompt)  # Utiliser le début du message comme titre
        st.session_state.conversation_id = create_conversation(title=title)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(conversation_id=st.session_state.conversation_id, role="user", content=prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    ###################
    #### Guardrail ####
    ###################

    try:
        guardrail = Guardrail()
    except Exception as e:
        st.error(f"Guardrail not found. Please re-run the container for regeneration. Details : {e}")
        st.stop()
    # is_supported = await guardrail.analyze_language(prompt)
    # if not is_supported:
    #     st.warning("To use our bot in a safe manner, you must do the conversation in either english, french, german or spanish. If necessary you may use an online translator.")
    #     st.stop()
    is_safe = guardrail.analyze_query(prompt)
    if not is_safe:
        st.warning("The promt seems to violate our ethical considerations. We invite you to ask a different question.")
        st.stop()

    ####################
    ###### PROMPT ######
    ####################

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
        save_message(conversation_id=st.session_state.conversation_id, role="assistant", content=response)





