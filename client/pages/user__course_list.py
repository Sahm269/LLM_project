import streamlit as st
import pandas as pd
import unicodedata
from server.db.dbmanager import get_db_manager

def normalize_text(text):
    """Normalise un texte en supprimant les accents et en le mettant en minuscules"""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8").strip().lower()
    return text

def course_list():
    # Récupérer l'ID utilisateur
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("⚠️ Vous devez être connecté pour voir votre liste de courses.")
        return

    # Charger la base de données
    db_manager = get_db_manager()
    
    # Charger les recettes et leurs ingrédients depuis la base de données
    query = "SELECT repas_suggestion, ingredients FROM suggestions_repas WHERE id_utilisateur = ?"
    raw_recipes = db_manager.execute_safe(query, (user_id,), fetch=True)

    if not raw_recipes:
        st.warning("⚠️ Aucune recette enregistrée pour générer une liste de courses.")
        return

    # ✅ Normalisation et suppression des doublons
    recipes = {}
    formatted_titles = {}

    for recipe in raw_recipes:
        title, ingredients = recipe["repas_suggestion"], recipe["ingredients"]
        normalized_title = normalize_text(title)

        if normalized_title not in recipes or (not recipes[normalized_title] and ingredients):
            recipes[normalized_title] = ingredients
            formatted_titles[normalized_title] = title

    recipe_titles = list(formatted_titles.values())

    # Sélectionner des recettes
    selected_recipes = st.multiselect("📌 Sélectionnez une ou plusieurs recettes", recipe_titles)

    # Initialiser all_ingredients pour éviter UnboundLocalError
    all_ingredients = []

    # Récupérer les ingrédients des recettes sélectionnées
    selected_ingredients = []
    for recipe in selected_recipes:
        normalized_recipe = normalize_text(recipe)
        ingredients = recipes.get(normalized_recipe)
        if ingredients:
            selected_ingredients.extend(ingredients.split(", "))

    # ✅ Option pour afficher la liste complète de courses
    if st.checkbox("👀 Afficher la liste complète des courses"):
        all_ingredients = list({ing for ing_list in recipes.values() if ing_list for ing in ing_list.split(", ")})

    # Affichage des ingrédients récupérés
    ingredients_to_display = selected_ingredients if selected_ingredients else all_ingredients
    if ingredients_to_display:
        st.subheader("📋 Ingrédients nécessaires")
        for ingredient in ingredients_to_display:
            st.write(f"🛒 {ingredient}")
    else:
        st.warning("⚠️ Aucun ingrédient enregistré.")

    # 📥 Exporter la liste des courses
    df = pd.DataFrame({"Ingrédients": ingredients_to_display})

    if st.download_button(
            label="📥 Télécharger la liste des courses",
            data=df.to_csv(index=False, sep=";").encode("utf-8-sig"),
            file_name="liste_courses.csv",
            mime="text/csv"):
        st.success("✅ Liste des courses exportée en CSV avec succès !")
