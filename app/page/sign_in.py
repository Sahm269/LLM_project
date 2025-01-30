import streamlit as st
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv

def sign_in(navigate_to):

    st.markdown(
        """
        <style>

        body, .stApp {
            background: linear-gradient(to right, #cae7d4, #a8d8b9);
        } 

        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        .stImage {
            animation: fadeIn 1s ease-in;
        }







        .stTextInput > div > div > input {
            font-size: 16px;
            border-radius: 8px;
            border: 1px solid #4CAF50;
        }

        .stButton > button {
            background-color: #4CAF50;
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
            box-shadow: 0px 0px 4px 4px rgba(132, 200, 156, 0.7);
        }

        .stAlert {
            text-align: center;
            font-weight: bold;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    logo_path = "assets/logo.png"

    # Créez trois colonnes et placez l'image dans la colonne du centre
    col1, col2, col3 = st.columns([1.5, 1.5, 1])  # La colonne centrale aura une largeur plus grande

    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)  # Ajustez la largeur selon la taille de votre logo

    # Récupération du gestionnaire de base de données (déjà stocké en session)
    db_manager = st.session_state.get("db_manager")

    # Titre de la page de connexion
    st.title("Connexion")

    # Champs de connexion
    login = st.text_input("👤 Pseudo")  # Champ pseudo
    password = st.text_input("🔒 Mot de passe", type="password")  # Champ mot de passe

    # Lien vers l'inscription
    if st.button("Pas de compte ? Inscrivez-vous.") :
        navigate_to("inscription")  # Redirection vers l'inscription

    # Bouton de connexion
    if st.button("Se connecter"):
        # Vérification des identifiants en base de données
        user = db_manager.fetch_by_condition("utilisateurs", "login = %s", (login,))

        if user:
            user_id = user[0][0]  # Récupération de l'ID utilisateur
            hashed_password = user[0][2]  # Récupération du mot de passe hashé

            # Vérification du mot de passe
            if check_password_hash(hashed_password, password):
                # Stocker les infos utilisateur dans la session
                st.session_state["logged_in"] = True
                st.session_state["user"] = login
                st.session_state["user_id"] = user_id

                # Message de confirmation
                st.success("✅ Connexion réussie ! Redirection en cours...")
                navigate_to("accueil")  # Redirige vers la page d'accueil
            else:
                st.error("❌ Mot de passe incorrect.")  # Message d'erreur si mauvais mot de passe
        else:
            st.error("❌ Utilisateur non trouvé.")  # Message d'erreur si login inexistant
