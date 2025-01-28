import streamlit as st
import sys
import os

# Charger dynamiquement les fichiers Python associés aux onglets
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'page')))
from info_perso import info_perso
from mealplan import mealplan
from course_list import course_list
from favoris import favoris

# Titre de la page User
st.title(f"Bienvenue {st.session_state['user']} !")

# Définition des onglets horizontaux
tabs = st.tabs(["🧑‍💼 Informations personnelles ", "🍽️ Meal Plan", "🛒 Liste des courses", "⭐ Favoris"])

# Onglet 1 : Informations personnelles
with tabs[0]:
    st.header("Informations personnelles")
    info_perso()  # Charger la page `info_perso.py`

# Onglet 2 : Meal Plan
with tabs[1]:
    st.header("Meal Plan")
    mealplan()  # Charger la page `mealplan.py`

# Onglet 3 : Liste des courses
with tabs[2]:
    st.header("Liste des courses")
    course_list()  # Charger la page `course_list.py`

# Onglet 4 : Favoris
with tabs[3]:
    st.header("Favoris")
    favoris()  # Charger la page `favoris.py`

