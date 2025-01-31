import streamlit as st
import sys
import os
from dotenv import load_dotenv


# Ajouter les chemins des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'page')))
from sign_in import sign_in
from sign_up import sign_up

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
from dbmanager import DBManager

# Charger les variables d'environnement
load_dotenv()
st.set_page_config(page_title="Nutrigénie", layout="wide")

# Configuration de la base de données
db_config = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Mettre DBManager en cache
@st.cache_resource
def get_db_manager():
    return DBManager(db_config, "../data/schema.json")

# Initialiser DBManager dans st.session_state si non défini
if "db_manager" not in st.session_state:
    st.session_state["db_manager"] = get_db_manager()

# Initialisation de la session utilisateur
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "connexion"
if "user" not in st.session_state:
    st.session_state["user"] = None

# Fonction de navigation
def navigate_to(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()

# Gestion de la déconnexion
def logout_user():
    keys_to_clear = ["logged_in", "user", "current_page"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    navigate_to("connexion")

# Gestion centralisée de la navigation
def handle_navigation():
    if not st.session_state["logged_in"]:
        # Redirection vers connexion si non connecté
        if st.session_state["current_page"] not in ["connexion", "inscription"]:
            st.session_state["current_page"] = "connexion"
            st.rerun()
    else:
        # Gestion des pages disponibles pour les utilisateurs connectés
        available_pages = ["accueil", "chatbot", "dashboard", "user"]
        if st.session_state["current_page"] not in available_pages:
            st.session_state["current_page"] = "accueil"
            st.rerun()

# Définition des pages disponibles
PAGES = {
    "accueil": {"file": "page/accueil.py", "title": "🏠 Accueil"},
    "chatbot": {"file": "page/chatbot.py", "title": "🤖 Chat Bot"},
    "dashboard": {"file": "page/dashboard.py", "title": "📊 Tableau de Bord"},
    "user": {"file": "page/user.py", "title": lambda: f"👤 Mon Compte {st.session_state.get('user', '')}"}
}

# Fonction principale
def main():

    st.markdown(
            """
            <style>


            .stButton > button {
                background-color: #6A5ACD;
                color: white;
                font-size: 18px;
                padding: 10px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                transition: 0.3s;
            }
            
            .stButton > button:hover {
                background-color: #388E3C;
                box-shadow: 0px 0px 1px 1px;
                color: white;
            }

            </style>
            """,
            unsafe_allow_html=True
        )

    # Gestion de la navigation
    handle_navigation()

    # Si l'utilisateur est connecté
    if st.session_state["logged_in"]:
        pages = []
        for page_name, page_info in PAGES.items():
            title = page_info["title"]
            if callable(title):  # Si le titre est une fonction
                title = title()
            pages.append(st.Page(page_info["file"], title=title))

        # Afficher la barre latérale et gérer la déconnexion
        with st.sidebar:
            if st.button("Déconnexion"):
                logout_user()

        # Navigation entre les pages
        pg = st.navigation(pages)
        pg.run()

    else:
        # Ne pas afficher la barre de navigation
        if st.session_state["current_page"] == "connexion":
            sign_in(navigate_to)
            
        elif st.session_state["current_page"] == "inscription":
            sign_up(navigate_to)

if __name__ == "__main__":
    main()
