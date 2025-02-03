import streamlit as st
import psycopg2
import sqlite3
from sqlite3 import Connection
from datetime import datetime
import logging
from typing import List, Dict
import pandas as pd

# Configuration du logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


# Fonction pour obtenir la connexion à la base de données
# def get_db_connection():
#     try:
#         conn = psycopg2.connect(
#             host=st.secrets["DB_HOST"],
#             port=st.secrets["DB_PORT"],
#             dbname=st.secrets["DB_NAME"],
#             user=st.secrets["DB_USER"],
#             password=st.secrets["DB_PASSWORD"]
#         )
#         return conn
#     except Exception as e:
#         logger.error(f"Erreur de connexion à la base de données: {e}")
#         return None


def get_db_connection() -> Connection:
    """
    Établit une connexion avec la base SQLite.

    Returns:
        Connection : le client de connexion à la base.
    """
    try:
        conn = sqlite3.connect(
            st.secrets["DB_NAME"], check_same_thread=False
        )  # Spécifiez ici le chemin de votre fichier SQLite
        conn.row_factory = sqlite3.Row  # Pour des résultats sous forme de dictionnaire
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erreur de connexion à la base de données SQLite: {e}")
        return None


# Connexion à la base de données pour récupérer le nombre total de recettes
# def get_recipes_count():
#     conn = get_db_connection()
#     if conn is None:
#         return 0
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT COUNT(*) FROM suggestions_repas")
#         result = cursor.fetchone()
#         return result[0]  # Le nombre total de recettes
#     except Exception as e:
#         logger.error(f"Erreur lors de la récupération du nombre de recettes : {e}")
#         return 0
#     finally:
#         cursor.close()
#         conn.close()


def get_recipes_count() -> int:
    """
    Récupère le nombre total de recettes enregistrées dans la table `suggestions_repas` de la base de données SQLite.
    
    Cette fonction se connecte à la base de données SQLite, exécute une requête pour compter le nombre d'entrées
    dans la table `suggestions_repas`, puis retourne ce nombre.
    
    Returns:
        int: Le nombre total de recettes dans la table `suggestions_repas`. Retourne 0 en cas d'erreur ou si la connexion échoue.
    """
    # Connexion à la base de données SQLite
    conn = get_db_connection()

    # Si la connexion échoue, on retourne 0
    if conn is None:
        return 0

    try:
        # Création du curseur pour exécuter la requête
        cursor = conn.cursor()

        # Exécution de la requête SQL pour compter les entrées de recettes dans la table 'suggestions_repas'
        cursor.execute("SELECT COUNT(*) FROM suggestions_repas")

        # Récupération du résultat de la requête
        result = cursor.fetchone()

        # Retour du nombre total de recettes
        return result[0]  # Le nombre total de recettes

    except sqlite3.Error as e:
        # En cas d'erreur, on enregistre l'erreur dans les logs et on retourne 0
        logger.error(f"Erreur lors de la récupération du nombre de recettes : {e}")
        return 0

    finally:
        # Fermeture du curseur et de la connexion
        cursor.close()
        conn.close()


# Fonction pour récupérer la latence moyenne des messages
# def get_average_latency():
#     conn = get_db_connection()
#     if conn is None:
#         return 0.0
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT AVG(temps_traitement) FROM messages WHERE temps_traitement IS NOT NULL")
#         result = cursor.fetchone()
#         return round(result[0], 2) if result[0] is not None else 0.0
#     except Exception as e:
#         logger.error(f"Erreur de connexion à la base de données pour la latence : {e}")
#         return 0.0
#     finally:
#         cursor.close()
#         conn.close()


def get_average_latency() -> float:
    """
    Récupère la latence moyenne des traitements enregistrés dans la table `messages` de la base de données SQLite.
    
    Cette fonction se connecte à la base de données SQLite, exécute une requête pour calculer la moyenne des valeurs 
    dans la colonne `temps_traitement` de la table `messages`, et retourne cette moyenne avec une précision de deux décimales.
    
    Returns:
        float: La latence moyenne des traitements en secondes. Retourne 0.0 en cas d'erreur ou si aucune donnée valide n'est disponible.
    """
    # Connexion à la base de données SQLite
    conn = get_db_connection()

    # Si la connexion échoue, on retourne 0.0
    if conn is None:
        return 0.0

    try:
        # Création du curseur pour exécuter la requête
        cursor = conn.cursor()

        # Exécution de la requête SQL pour calculer la moyenne de la colonne 'temps_traitement'
        cursor.execute(
            "SELECT AVG(temps_traitement) FROM messages WHERE temps_traitement IS NOT NULL"
        )

        # Récupération du résultat de la requête
        result = cursor.fetchone()

        # Retour de la moyenne arrondie à 2 décimales, ou 0.0 si aucun résultat
        return round(result[0], 2) if result[0] is not None else 0.0

    except sqlite3.Error as e:
        # En cas d'erreur, on enregistre l'erreur dans les logs et on retourne 0.0
        logger.error(f"Erreur de connexion à la base de données pour la latence : {e}")
        return 0.0

    finally:
        # Fermeture du curseur et de la connexion
        cursor.close()
        conn.close()


# Fonction pour récupérer le nombre de requêtes par jour
# def get_daily_requests():
#     conn = get_db_connection()
#     if conn is None:
#         return pd.DataFrame()
#     try:
#         query = """
#         SELECT
#             DATE(timestamp) AS date,
#             COUNT(*) AS nombre_requetes
#         FROM
#             messages
#         GROUP BY
#             date
#         ORDER BY
#             date;
#         """
#         df = pd.read_sql(query, conn)
#         return df
#     except Exception as e:
#         logger.error(f"Erreur lors de la récupération des requêtes par jour : {e}")
#         return pd.DataFrame()
#     finally:
#         conn.close()


def get_daily_requests() -> pd.DataFrame:
    """
    Récupère les requêtes quotidiennes à partir de la table `messages` de la base de données SQLite.
    
    Cette fonction se connecte à la base de données SQLite, exécute une requête SQL pour compter le nombre de requêtes
    (messages) par jour, et retourne les résultats sous forme de DataFrame pandas.
    
    Returns:
        pd.DataFrame: Un DataFrame contenant les dates et le nombre de requêtes pour chaque jour. 
                      Retourne un DataFrame vide en cas d'erreur.
    """
    # Connexion à la base de données SQLite
    conn = get_db_connection()

    # Si la connexion échoue, retourner un DataFrame vide
    if conn is None:
        return pd.DataFrame()

    try:
        # Requête SQL pour récupérer le nombre de requêtes par jour
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

        # Exécution de la requête et récupération du résultat sous forme de DataFrame
        df = pd.read_sql(query, conn)

        # Retour du DataFrame contenant les résultats
        return df

    except sqlite3.Error as e:
        # En cas d'erreur, on enregistre l'erreur dans les logs et on retourne un DataFrame vide
        logger.error(f"Erreur lors de la récupération des requêtes par jour : {e}")
        return pd.DataFrame()

    finally:
        # Fermeture de la connexion à la base de données
        conn.close()


# Fonction pour récupérer les ingrédients depuis la base de données
# def get_ingredients():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute("SELECT ingredients FROM liste_courses")
#         ingredients_list = cursor.fetchall()  # Récupère tous les résultats
#         return ingredients_list
#     except Exception as e:
#         logger.error(f"Erreur lors de la récupération des requêtes par jour : {e}")
#         return pd.DataFrame()
#     finally:
#         # Fermer la connexion
#         cursor.close()
#         conn.close()


def get_ingredients() -> list:
    """
    Récupère la liste des ingrédients stockée dans la table `liste_courses` de la base de données SQLite.

    Cette fonction se connecte à la base de données SQLite, exécute une requête SQL pour récupérer la colonne `ingredients`
    de la table `liste_courses`, et retourne les résultats sous forme de liste.

    Returns:
        list: Une liste contenant les ingrédients récupérés de la base de données. 
              Retourne une liste vide en cas d'erreur.
    """
    # Connexion à la base de données SQLite
    conn = get_db_connection()

    # Si la connexion échoue, retourner une liste vide
    if conn is None:
        return []

    cursor = conn.cursor()

    try:
        # Requête SQL pour récupérer la colonne 'ingredients' de la table 'liste_courses'
        cursor.execute("SELECT ingredients FROM liste_courses")

        # Récupère tous les résultats de la requête
        ingredients_list = cursor.fetchall()

        # Retourne la liste des ingrédients (sous forme de liste de tuples)
        return [ingredient[0] for ingredient in ingredients_list]

    except sqlite3.Error as e:
        # En cas d'erreur, on enregistre l'erreur dans les logs et on retourne une liste vide
        logger.error(f"Erreur lors de la récupération des ingrédients : {e}")
        return []

    finally:
        # Fermeture du curseur et de la connexion à la base de données
        cursor.close()
        conn.close()


# Fonction pour récupérer le coût total des requêtes
# def get_total_cost():
#     conn = get_db_connection()
#     if conn is None:
#         return 0.0
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT SUM(total_cout) FROM messages WHERE total_cout IS NOT NULL")
#         result = cursor.fetchone()
#         return round(result[0], 2) if result[0] is not None else 0.0
#     except Exception as e:
#         logger.error(f"Erreur lors de la récupération du coût total : {e}")
#         return 0.0
#     finally:
#         cursor.close()
#         conn.close()


def get_total_cost() -> float:
    """
    Récupère le coût total des messages dans la table `messages` de la base de données SQLite.

    Cette fonction se connecte à la base de données SQLite, exécute une requête SQL pour récupérer la somme des valeurs 
    présentes dans la colonne `total_cout` de la table `messages`, et retourne le total arrondi à 2 décimales.

    Returns:
        float: Le coût total des messages. Retourne 0.0 si aucune donnée n'est disponible ou en cas d'erreur.
    """
    # Connexion à la base de données SQLite
    conn = get_db_connection()

    # Si la connexion échoue, retourner 0.0
    if conn is None:
        return 0.0

    cursor = conn.cursor()

    try:
        # Requête SQL pour récupérer la somme de la colonne 'total_cout' de la table 'messages'
        cursor.execute(
            "SELECT SUM(total_cout) FROM messages WHERE total_cout IS NOT NULL"
        )

        # Récupère le résultat de la requête
        result = cursor.fetchone()

        # Retourne la somme arrondie à 2 décimales si un résultat est trouvé, sinon retourne 0.0
        return round(result[0], 2) if result[0] is not None else 0.0

    except sqlite3.Error as e:
        # En cas d'erreur, on log l'erreur et on retourne 0.0
        logger.error(f"Erreur lors de la récupération du coût total : {e}")
        return 0.0

    finally:
        # Fermeture du curseur et de la connexion à la base de données
        cursor.close()
        conn.close()


# Fonction pour récupérer l'impact écologique estimé
# def get_total_impact():
#     conn = get_db_connection()
#     if conn is None:
#         return 0.0
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT SUM(impact_eco) FROM messages WHERE impact_eco IS NOT NULL")
#         result = cursor.fetchone()
#         return round(result[0], 2) if result[0] is not None else 0.0
#     except Exception as e:
#         logger.error(f"Erreur lors de la récupération de l'impact écologique : {e}")
#         return 0.0
#     finally:
#         cursor.close()
#         conn.close()


def get_total_impact() -> float:
    """
    Récupère l'impact écologique total des messages dans la table `messages` de la base de données SQLite.

    Cette fonction se connecte à la base de données SQLite, exécute une requête SQL pour récupérer la somme des valeurs 
    présentes dans la colonne `impact_eco` de la table `messages`, et retourne le total arrondi à 2 décimales.

    Returns:
        float: L'impact écologique total des messages. Retourne 0.0 si aucune donnée n'est disponible ou en cas d'erreur.
    """
    # Connexion à la base de données SQLite
    conn = get_db_connection()

    # Si la connexion échoue, retourner 0.0
    if conn is None:
        return 0.0

    cursor = conn.cursor()

    try:
        # Requête SQL pour récupérer la somme de la colonne 'impact_eco' de la table 'messages'
        cursor.execute(
            "SELECT SUM(impact_eco) FROM messages WHERE impact_eco IS NOT NULL"
        )

        # Récupère le résultat de la requête
        result = cursor.fetchone()

        # Retourne la somme arrondie à 2 décimales si un résultat est trouvé, sinon retourne 0.0
        return round(result[0], 2) if result[0] is not None else 0.0

    except sqlite3.Error as e:
        # En cas d'erreur, on log l'erreur et on retourne 0.0
        logger.error(f"Erreur lors de la récupération de l'impact écologique : {e}")
        return 0.0

    finally:
        # Fermeture du curseur et de la connexion à la base de données
        cursor.close()
        conn.close()
