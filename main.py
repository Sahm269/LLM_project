# data_link = https://github.com/Sahm269/LLM_project/tree/souraya/data
import streamlit as st

# from streamlit_option_menu import option_menu
# from client.pages.home import home_page
# from projects.LLM_project.client.pages.nutri_old import nutri_page
# from client.pages.dashboard import dashboard_page
# from client.pages.about import about_page
from client.pages.sign_in import sign_in
from client.pages.sign_up import sign_up
from server.db.dbmanager import get_db_manager

APP_TITLE = "Nutrigénie"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="client/assets/avatar_bot_small.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# with st.sidebar:
#     st.image("client/assets/avatar_bot_medium.jpg")

#     selected = option_menu(
#         menu_title='',
#         options=["Accueil", "Nutrigénie", "Tableau de bord", "A propos"],
#         icons=["house", "patch-question", "bar-chart", "info-circle"],
#         default_index=0,
#         # orientation="horizontal",
#     )

# if selected == "Accueil":
#     home_page()
# elif selected == "Nutrigénie":
#     nutri_page()
# elif selected == "Tableau de bord":
#     dashboard_page()
# elif selected == "A propos":
#     about_page()

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
    "accueil": {"file": "client/pages/home.py", "title": "🏠 Accueil"},
    "chatbot": {"file": "client/pages/nutri.py", "title": "🤖 Chat Bot"},
    "dashboard": {"file": "client/pages/dashboard.py", "title": "📊 Tableau de Bord"},
    "user": {
        "file": "client/pages/user.py",
        "title": lambda: f"👤 Mon Compte {st.session_state.get('user', '')}",
    },
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
        unsafe_allow_html=True,
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
