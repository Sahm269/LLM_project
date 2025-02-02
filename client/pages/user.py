import streamlit as st
from client.pages.user__info_perso import info_perso
from client.pages.user__mealplan import mealplan
from client.pages.user__course_list import course_list
from client.pages.user__favoris import favoris


# Appliquer le style personnalisé aux headers
st.markdown("""
    <style>
        /* Style global pour les headers */
        h3 {
            font-size: 20px;
            font-family: New Icon;
            font-weight: 700;
        }
            
        h2 {
            font-size: 2rem;
            color: #2a4b47;
        }

        .welcome-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2a4b47;
            text-align: center;
            animation: fadeIn 2s ease-out;
        }

        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        .user-name {
            color: #4e7a63;
            font-size: 3rem;
            font-weight: bold;
            animation: nameAnimation 2s ease-out;
            font-family: New Icon;
        }
    </style>
""", unsafe_allow_html=True)

# Affichage du message de bienvenue
st.markdown(f"""
    <h2 class="welcome-title">
        Bienvenue sur NutriGénie <span class="user-name">{st.session_state['user']}</span> 🍽️!
    </h2>
""", unsafe_allow_html=True)

# Définition des onglets horizontaux
tabs = st.tabs(["🧑‍💼 Informations personnelles ", "🍽️ Meal Plan", "🛒 Liste des courses", "⭐ Favoris"])

# Onglet 1 : Informations personnelles
with tabs[0]:
    st.markdown('<h3 class="stHeader">🧑‍💼 Informations personnelles</h3>', unsafe_allow_html=True)
    info_perso()  # Charger la page `info_perso.py`

# Onglet 2 : Meal Plan
with tabs[1]:
    st.markdown('<h3 class="stHeader">🍽️ Meal Plan</h3>', unsafe_allow_html=True)
    mealplan()  # Charger la page `mealplan.py`

# Onglet 3 : Liste des courses
with tabs[2]:
    st.markdown('<h3 class="stHeader">🛒 Liste des courses</h3>', unsafe_allow_html=True)
    course_list()  # Charger la page `course_list.py`

# Onglet 4 : Favoris
with tabs[3]:
    st.markdown('<h3 class="stHeader">⭐ Favoris</h3>', unsafe_allow_html=True)
    favoris()  # Charger la page `favoris.py`
