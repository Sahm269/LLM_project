import streamlit as st
import sqlite3
from mistralai import Mistral
from datetime import datetime
import time
import numpy as np


# Configuration de la base de données SQLite
DB_NAME = "chat_history.db"
conversation_id = None

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
    c.execute("SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation_id,)) #Peut etre à sort par datetime ?
    data = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return data

def load_conversations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM conversations ORDER BY created_at DESC") #Peut etre à sort par datetime ?
    data = c.fetchall()
    conn.close()
    return data



# Initialisation du client Mistral
api_key = "RXjfbTO7wkOU0RwrwP7XpFfcj1K5eq40"
mistral_client = Mistral(api_key=api_key)

# Initialisation de la base de données
init_db()

# Interface Streamlit
st.set_page_config(page_title="Nutrigénie", layout="wide")
# Diviser la page en deux colonnes pour simuler deux barres latérales
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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Dîtes quelque-chose"):
    if st.session_state.conversation_id is None:
        title = prompt[:30]  # Utiliser le début du message comme titre
        st.session_state.conversation_id = create_conversation(title=title)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(conversation_id=st.session_state.conversation_id, role="user", content=prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream_response = mistral_client.chat.stream(
            model=st.session_state["mistral_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )
        response = ""
        response_placeholder = st.empty()
        for chunk in stream_response:
            response += chunk.data.choices[0].delta.content
            response_placeholder.markdown(response)
            time.sleep(0.03)
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_message(conversation_id=st.session_state.conversation_id, role="assistant", content=response)

# Section pour afficher l'historique de la conversation
conversation_history = load_conversations()

st.sidebar.title("Navigation")

# Barre latérale : Liste des conversations
st.sidebar.title("Historique")
for conversation_id,_, title in conversation_history:
    if st.sidebar.button(title):
        # Charger la conversation sélectionnée
        st.session_state.conversation_id = conversation_id
        st.session_state.messages = load_messages(conversation_id)
        st.rerun()




