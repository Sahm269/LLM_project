import streamlit as st
import base64

st.set_page_config(page_title="NutriGénie", page_icon="assets/logo.png", layout="wide")


def add_logo():

    # Lecture du fichier image local
    with open("assets/logo.png", "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url("data:image/png;base64,{logo_data}");
                background-repeat: no-repeat;
                padding-top: 275px;
                background-position: center 20px;
                background-size: 50%;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


add_logo()
# Définition des onglets

# Définition des onglets
accueil = st.Page("onglets/accueil.py", title="🏠 Accueil")
chatbot = st.Page("onglets/chatbot.py", title="📊 Chat Bot")
course_list = st.Page("onglets/mealplan.py", title="🛒 Weekly meal")
historique = st.Page("onglets/historique.py", title="📜 Historique de repas")
dashboard = st.Page("onglets/dashboard.py", title="📊 Tableau de bord")

pg = st.navigation([accueil, chatbot, course_list, historique, dashboard])
pg.run()
