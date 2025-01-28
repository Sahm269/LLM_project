import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'page')))
from sign_in import sign_in
from sign_up import sign_up

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
from dotenv import load_dotenv
from dbmanager import DBManager  

# Charger les variables d'environnement
load_dotenv()

# Configuration de la base de données
db_config = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Initialiser DBManager dans `st.session_state` si non défini
if "db_manager" not in st.session_state:
    st.session_state["db_manager"] = DBManager(db_config, "../data/schema.json")



# Fonction pour mettre à jour l'URL avec la page courante
def update_url(page_name):
    st.query_params["page"] = page_name

# Gestion de la session utilisateur
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_page" not in st.session_state:
    current_page = st.query_params.get("page", "connexion")
    st.session_state["current_page"] = current_page

# Fonction pour la navigation
def navigate_to(page_name):
    st.session_state["current_page"] = page_name
    update_url(page_name)  # Met à jour l'URL

def main():
    # Vérifier si l'utilisateur est connecté
    if st.session_state["logged_in"]:
        

        # Définition des onglets
        accueil = st.Page("page/accueil.py", title="Accueil")
        chatbot = st.Page("page/chatbot.py", title="Chat Bot")
        dashboard = st.Page("page/dashboard.py", title="Tableau de bord")
        user = st.Page("page/user.py", title=  f"mon compte {st.session_state['user']}")

        with st.sidebar:
            if st.button("Déconnexion"):
                st.session_state["logged_in"] = False
                st.session_state["current_page"] = "connexion"
                update_url("connexion") 

        pg = st.navigation([accueil, chatbot, user, dashboard])
        pg.run()
       
           
    else:
        # Ne pas afficher la navbar sur les pages de connexion et d'inscription
        if st.session_state["current_page"] == "connexion":
            sign_in(navigate_to)
        elif st.session_state["current_page"] == "inscription":
            sign_up(navigate_to)

if __name__ == "__main__":
    main()
