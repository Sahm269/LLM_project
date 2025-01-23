import streamlit as st
import sqlite3
from mistralai import Mistral

# Configuration de la base de données SQLite
DB_NAME = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL
                 )''')
    conn.commit()
    conn.close()

def save_to_db(role, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (role, message) VALUES (?, ?)", (role, message))
    conn.commit()
    conn.close()

def load_conversation():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, message FROM conversations")
    data = c.fetchall()
    conn.close()
    return data

# Initialisation du client Mistral
api_key = "RXjfbTO7wkOU0RwrwP7XpFfcj1K5eq40"
model = "mistral-large-latest"
mistral_client = Mistral(api_key=api_key)

def get_response_from_mistral(conversation):
    try:
        # Crée une liste de messages dans le format attendu par Mistral
        messages = [
            {"role": "user" if role == "user" else "assistant", "content": message}
            for role, message in conversation
        ]

        stream_response = mistral_client.chat.stream(
            model=model,
            messages=messages
        )

        bot_response = ""
        for chunk in stream_response:
            bot_response += chunk.data.choices[0].delta.content

        return bot_response
    except Exception as e:
        return f"Error: {e}"

# Initialisation de la base de données
init_db()

# Interface Streamlit
st.set_page_config(page_title="Chat with Mistral", layout="wide")
st.title("Chat with Mistral")

# Section pour afficher l'historique de la conversation
conversation_history = load_conversation()

st.sidebar.title("Conversation History")
for role, message in conversation_history:
    if role == "user":
        with st.sidebar.expander(f"You: {message[:30]}..."):
            st.write(f"You: {message}")
    else:
        st.sidebar.write(f"Mistral: {message}")

# Champ de saisie utilisateur
user_input = st.text_input("Type your message:", placeholder="Ask me anything!")

# Bouton d'envoi
if st.button("Send"):
    if user_input.strip():
        # Ajouter le message utilisateur à l'historique
        save_to_db("user", user_input)

        # Charger l'historique complet pour le contexte
        full_conversation = load_conversation()

        # Obtenir une réponse de Mistral
        bot_response = get_response_from_mistral(full_conversation)

        # Ajouter la réponse du bot à l'historique
        save_to_db("assistant", bot_response)

        # Afficher la réponse
        st.markdown(f"**You:** {user_input}")
        st.markdown(f"**Mistral:** {bot_response}")
    else:
        st.warning("Please enter a message before sending.")

# Affichage en temps réel des messages
st.subheader("Live Conversation")
for role, message in reversed(conversation_history):
    if role == "user":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Mistral:** {message}")
