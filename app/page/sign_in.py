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
        # Récupère l'utilisateur correspondant au login
        user = db_manager.fetch_by_condition("utilisateurs", "login = %s", (login,))  # login est ton input utilisateur
        if user:
            user_id = user[0][0]  # Supposons que 'id' est la première colonne
            hashed_password = user[0][2]  # Supposons que 'mot_de_passe' est la 3ème colonne
            
            # Vérifie le mot de passe
            if check_password_hash(hashed_password, password):
                # Stocke les informations utilisateur dans la session
                st.session_state["logged_in"] = True
                st.session_state["user"] = login
                st.session_state["user_id"] = user_id  # Ajout de l'ID dans la session
                st.success("Connexion réussie, recliquez sur le bouton pour accéder à votre session !.")
                navigate_to("accueil")
            else:
                st.error("Mot de passe incorrect.")
        else:
            st.error("Utilisateur non trouvé.")
