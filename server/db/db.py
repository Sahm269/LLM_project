import streamlit as st
import psycopg2
from datetime import datetime
import logging
from typing import List, Dict
import pandas as pd

# Configuration du logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)



# Fonction pour obtenir la connexion à la base de données
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            # port=os.getenv("DB_PORT"),
            dbname=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"]
        )
        return conn
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Connexion à la base de données pour récupérer le nombre total de recettes
def get_recipes_count():
    conn = get_db_connection()
    if conn is None:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recettes")
        result = cursor.fetchone()
        return result[0]  # Le nombre total de recettes
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du nombre de recettes : {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

# Fonction pour récupérer la latence moyenne des messages
def get_average_latency():
    conn = get_db_connection()
    if conn is None:
        return 0.0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(temps_traitement) FROM messages WHERE temps_traitement IS NOT NULL")
        result = cursor.fetchone()
        return round(result[0], 2) if result[0] is not None else 0.0
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données pour la latence : {e}")
        return 0.0
    finally:
        cursor.close()
        conn.close()

# Fonction pour récupérer le nombre de requêtes par jour
def get_daily_requests():
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        query = """
        SELECT
            DATE(timestamp) AS date,
            COUNT(*) AS nombre_requetes
        FROM
            messages
        GROUP BY
            date
        ORDER BY
            date;
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des requêtes par jour : {e}")
        return pd.DataFrame()
    finally:
        conn.close()


# Fonction pour récupérer les ingrédients depuis la base de données
def get_ingredients():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ingredients FROM liste_courses")
        ingredients_list = cursor.fetchall()  # Récupère tous les résultats
        return ingredients_list
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des requêtes par jour : {e}")
        return pd.DataFrame()
    finally:
        # Fermer la connexion
        cursor.close()
        conn.close()