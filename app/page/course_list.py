import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Fonction pour obtenir la connexion à la base de données
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Fonction pour récupérer les ingrédients depuis la base de données
def get_ingredients():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ingredients FROM liste_courses")
    ingredients_list = cursor.fetchall()  # Récupère tous les résultats
    
    # Fermer la connexion
    cursor.close()
    conn.close()
    
    return ingredients_list

# Page des courses
def course_list():
    st.write("Voici votre liste des courses.")
    
    ingredients_list = get_ingredients()
    
    if ingredients_list:
        for ingredient in ingredients_list:
            st.write(f"🍎 {ingredient[0]}")
    else:
        st.write("Aucun ingrédient trouvé.")

    st.checkbox("Ajouter un nouvel article")


