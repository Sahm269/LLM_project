import streamlit as st
import sqlite3
from mistralai import Mistral
from datetime import datetime
import logging
import platform
from dotenv import load_dotenv
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

if platform.system() == "Windows":
    # Specify the path to your .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    # Load the .env file
    load_dotenv(dotenv_path)
else:
    load_dotenv()




# Establish PostgreSQL connection
# try:
#     db = psycopg2.connect(
#         host=os.environ.get("POSTGRES_HOST"),
#         user=os.environ.get("POSTGRES_USER"),
#         password=os.environ.get("POSTGRES_PASSWORD"),
#         dbname=os.environ.get("POSTGRES_DBNAME"),
#         port=os.environ.get("POSTGRES_PORT")
#     )
# except psycopg2.OperationalError as err:
#     logger.error(f"Operational error: {err}")
# except psycopg2.Error as err:
#     logger.error(f"Database connection error: {err}")



# Configuration de la base de données SQLite
DB_NAME = "chat_history.db"
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
# Initialisation du client Mistral
# api_key = "RXjfbTO7wkOU0RwrwP7XpFfcj1K5eq40"
# api_key = os.environ.get("MISTRAL_API_KEY")
# mistral_client = Mistral(api_key=api_key)

def get_cursor():
    """
    Validate and obtain a cursor for database operations.

    Returns:
        cursor: A database cursor.
    """
    try:
        return conn.cursor()
    except sqlite3.Error as err:
        logger.error(f"Error obtaining cursor: {err}")
        return None
    

def init_db():
    cursor = get_cursor()
    try:
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    title TEXT NOT NULL
                )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        return
    except sqlite3.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        conn.commit()
        # conn.close()


def save_message(conversation_id, role, content):
    cursor = get_cursor()
    try:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute("INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, timestamp))
    except sqlite3.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return
        raise HTTPException(status_code=500, detail=str(err))
    finally:
        conn.commit()
        # conn.close()

def create_conversation(title):
    cursor = get_cursor()
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO conversations (created_at, title) VALUES (?, ?)", (created_at, title))
        conversation_id = cursor.lastrowid
        return conversation_id
    except sqlite3.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        raise Exception(status_code=500, detail=str(err))
    finally:
        conn.commit()
        # conn.close()
    

def load_messages(conversation_id):
    cursor = get_cursor()
    try:
        cursor.execute("SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation_id,))
        data = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        return data
    except sqlite3.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        raise Exception(status_code=500, detail=str(err))
    finally:
        conn.commit()
        # conn.close()

def load_conversations():
    cursor = get_cursor()
    try:
        cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC") 
        data = cursor.fetchall()
        return data
    except sqlite3.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        raise Exception(status_code=500, detail=str(err))
    finally:
        conn.commit()
        # conn.close()

def update_conversation(conversation_id):
    cursor = get_cursor()
    try:
        new_timer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE conversations SET created_at = ? WHERE id = ?",(new_timer, conversation_id))
    except sqlite3.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        raise Exception(status_code=500, detail=str(err))
    finally:
        conn.commit()
        # conn.close()