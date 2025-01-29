import streamlit as st
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

import sys



def sign_up(navigate_to):
    db_manager = st.session_state.get("db_manager")
    st.title("Inscription")
    login = st.text_input("Pseudo")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")

     # Lien pour rediriger vers la page d'inscription
    if st.button("Déjà un compte ? connectez-vous."):
        navigate_to("connexion")


    if st.button("Créer un compte"):
        if password != confirm_password:
            st.error("Les mots de passe ne correspondent pas.")
        else:
            hashed_password = generate_password_hash(password)
            try:
                db_manager.insert_data_from_dict("utilisateurs", [{
                    "login": login,
                    "email": email,
                    "mot_de_passe": hashed_password
                }],"id_utilisateur")
                st.success("Compte créé avec succès. Vous pouvez vous connecter.")
                st.session_state["current_page"] = "connexion"
            except Exception as e:
                st.error(f"Erreur lors de l'inscription : {e}")
