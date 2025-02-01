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

    #centrer le logo
    col1, col2, col3 = st.columns([1.5, 1.5, 1])

    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)

    # Récupération du gestionnaire de base de données (déjà stocké en session)
    db_manager = st.session_state.get("db_manager")

    st.title("Connexion")

    # Champs de connexion
    login = st.text_input("👤 Pseudo")
    password = st.text_input("🔒 Mot de passe", type="password")

    
    # Bouton de connexion
    if st.button("Se connecter"):
        # Vérification des identifiants en base de données
        user = db_manager.fetch_by_condition("utilisateurs", "login = %s", (login,))
        print("user",user)

        if user:
            user = user[0]
            user_id = user["id_utilisateur"] # Récupération de l'ID utilisateur
            hashed_password = user["mot_de_passe"]  # Récupération du mot de passe hashé

            # Vérification du mot de passe
            if check_password_hash(hashed_password, password):
                # Stocker les infos utilisateur dans la session
                st.session_state["logged_in"] = True
                st.session_state["user"] = login
                st.session_state["user_id"] = user_id

                # Message de confirmation
                st.success("✅ Connexion réussie !")
                navigate_to("accueil")  # Redirige vers la page d'accueil
            else:
                st.error("❌ Mot de passe incorrect.")
        else:
            st.error("❌ Utilisateur non trouvé.")

    # Lien vers l'inscription
    if st.button("Pas de compte ? Inscrivez-vous.") :
        navigate_to("inscription")  # Redirection vers l'inscription


"""
# Forcer la connexion pendant le développement (commenter cette partie si nécessaire)
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        # Simuler une connexion (utiliser des valeurs par défaut)
        st.session_state["logged_in"] = True
        st.session_state["user"] = "dev_user"
        st.session_state["user_id"] = 1  # ID fictif pour le développement
        st.success("✅ Connexion simulée pour le développement !")
        navigate_to("accueil")  # Redirige vers la page d'accueil
    else:
        # Logique de connexion normale (en production)
        login = st.text_input("👤 Pseudo")
        password = st.text_input("🔒 Mot de passe", type="password")

        if st.button("Se connecter"):
            user = db_manager.fetch_by_condition("utilisateurs", "login = %s", (login,))

            if user:
                user_id = user[0][0]
                hashed_password = user[0][2]

                if check_password_hash(hashed_password, password):
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = login
                    st.session_state["user_id"] = user_id
                    st.success("✅ Connexion réussie !")
                    navigate_to("accueil")
                else:
                    st.error("❌ Mot de passe incorrect.")
            else:
                st.error("❌ Utilisateur non trouvé.")

    if st.button("Pas de compte ? Inscrivez-vous."):
        navigate_to("inscription")
        """