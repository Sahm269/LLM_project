import streamlit as st
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
import sys


def sign_in(navigate_to):
    db_manager = st.session_state.get("db_manager")
    st.title("Connexion")
    login = st.text_input("Pseudo")
    password = st.text_input("Mot de passe", type="password")
    
    # Lien pour rediriger vers la page d'inscription
    if st.button("Pas de compte ? Inscrivez-vous."):
        navigate_to("inscription")

    if st.button("Se connecter"):
        user = db_manager.fetch_by_condition("utilisateurs", "login = %s", (login,))
        if user:
            hashed_password = user[0][2]  # Colonne mot_de_passe
            if check_password_hash(hashed_password, password):
                st.session_state["logged_in"] = True
                st.session_state["user"] = login
                st.success("Connexion réussie recliquez sur le bouton pour acceder à votre session !.")
                navigate_to("accueil")
               
            else:
                st.error("Mot de passe incorrect.")
        else:
            st.error("Utilisateur non trouvé.")
