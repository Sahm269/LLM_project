import sys 
import os
from mistralai import Mistral
from datetime import datetime
import time
import numpy as np
from mistralai.models.sdkerror import SDKError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
from dotenv import load_dotenv
from dbmanager import DBManager  


# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("api_key")
mistral_client = Mistral(api_key=api_key)



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
