import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from server.db.dbmanager import (
    get_db_manager,
    load_chatbot_suggestions
)
db_manager = get_db_manager()
user_id = st.session_state["user_id"]


def get_week_dates(year, week):
    """Retourne les dates du Lundi au Dimanche pour une semaine donnée."""
    first_day_of_year = datetime(year, 1, 1)
    first_monday = first_day_of_year + timedelta(days=(7 - first_day_of_year.weekday()))  # Trouver le premier lundi
    start_date = first_monday + timedelta(weeks=week - 1)  # Trouver le début de la semaine sélectionnée
    return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]  # 7 jours (Lundi → Dimanche)

def mealplan():
    # 📆 Sélection de l'année et de la semaine
    current_year = datetime.now().year
    current_week = datetime.now().isocalendar()[1]

    year_options = list(range(current_year, current_year - 3, -1))  # Années en ordre décroissant
    col1, col2 = st.columns([0.5, 0.5])  # Réduction de la largeur des sélecteurs
    with col1:
        selected_year = st.selectbox("📅 Année", year_options, index=0)
    with col2:
        week_options = [f"Semaine {i}" for i in range(1, 53)]
        selected_week_label = st.selectbox("📆 Semaine", week_options, index=week_options.index(f"Semaine {current_week}"))
        selected_week = int(selected_week_label.split(" ")[1])

    # 📌 Génération des 7 jours de la semaine sélectionnée
    week_dates = get_week_dates(selected_year, selected_week)

    # 📋 Initialisation des repas
    if "meal_plan" not in st.session_state:
        st.session_state["meal_plan"] = {}

    for date in week_dates:
        if date not in st.session_state["meal_plan"]:
            st.session_state["meal_plan"][date] = {
                "Petit-déjeuner": "", "Déjeuner": "", "Dîner": ""
            }

    # 📋 Affichage du planning pour 7 jours
    st.subheader(f"📆 Planning des repas - {selected_week_label} ({selected_year})")
    df = pd.DataFrame.from_dict({date: st.session_state["meal_plan"][date] for date in week_dates}, orient="index")
    df.index = pd.to_datetime(df.index).strftime("%A %d %B")  # Affichage clair des jours
    st.dataframe(df, use_container_width=True)

    # ✅ **Message de validation persistant**
    if "validation_msg" in st.session_state:
        st.success(st.session_state["validation_msg"])
        st.session_state.pop("validation_msg")  # Supprimer après affichage pour éviter la persistance infinie

    # 🍽️ **Modification et Suppression d'un Repas**
    st.subheader("✍️ Modifier un repas")

    selected_day = st.selectbox("📅 Choisissez un jour", week_dates)
    selected_meal = st.selectbox("🍽️ Sélectionnez le repas", ["Petit-déjeuner", "Déjeuner", "Dîner"])

    # 📌 **Prévisualisation du repas existant**
    existing_meal = st.session_state["meal_plan"][selected_day][selected_meal]
    if existing_meal:
        st.markdown(f"🔹 **Repas actuel pour {selected_meal} :**\n> {existing_meal}")

    with st.form("meal_form"):
        meal_input = st.text_area(f"Ajoutez un plat pour {selected_meal} ({selected_day})",
                                  value=existing_meal)  # Pré-rempli avec le repas actuel

        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            submitted = st.form_submit_button("✅ Ajouter / Modifier")
        with col2:
            deleted = st.form_submit_button("❌ Supprimer le plat")

        if submitted:
            st.session_state["meal_plan"][selected_day][selected_meal] = meal_input
            st.session_state["validation_msg"] = f"✅ {selected_meal} ajouté/modifié pour le {selected_day} avec succès !"
            st.rerun()

        if deleted:
            st.session_state["meal_plan"][selected_day][selected_meal] = ""
            st.session_state["validation_msg"] = f"❌ {selected_meal} supprimé pour le {selected_day} !"
            st.rerun()

    # 🤖 Ajout des suggestions du chatbot
    st.subheader("🤖 Suggestions du Chatbot")

    # 🔹 Charger les suggestions enregistrées si elles ne sont pas déjà en mémoire
    if "chatbot_suggestions" not in st.session_state:
        st.session_state["chatbot_suggestions"] = load_chatbot_suggestions(db_manager, user_id)


    if st.session_state["chatbot_suggestions"]:
        with st.form("chatbot_form"):
            selected_recipe = st.selectbox("🔍 Sélectionnez une recette", st.session_state["chatbot_suggestions"])
            selected_day_for_recipe = st.selectbox("📅 Assigner à quel jour ?", week_dates)
            selected_meal_for_recipe = st.selectbox("🍽️ Assigner à quel repas ?", ["Petit-déjeuner", "Déjeuner", "Dîner"])

            add_recipe = st.form_submit_button("➕ Ajouter la recette au planning")
            if add_recipe:
                st.session_state["meal_plan"][selected_day_for_recipe][selected_meal_for_recipe] += f"\n- {selected_recipe}"
                st.session_state["validation_msg"] = f"✅ Recette ajoutée à {selected_meal_for_recipe} ({selected_day_for_recipe}) avec succès !"
                st.rerun()
    else:
        st.write("⚠️ Aucune suggestion du chatbot pour le moment.")

    # 📤 Exportation du planning en CSV
    if st.button("📥 Exporter en CSV"):
        df.to_csv("meal_plan.csv")
        st.success("✅ Plan exporté en CSV avec succès !")
