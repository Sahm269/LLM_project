import streamlit as st

def main():
    st.set_page_config(page_title="Recettes Personnalisées", page_icon="🍴", layout="wide")

    # En-tête de l'application
    st.title("🍴 Recettes Personnalisées")
    st.subheader("Des recettes adaptées à vos objectifs nutritionnels")

    # Menu latéral
    with st.sidebar:
        st.header("Menu")
        mode = st.radio("Choisissez une option :", [
            "Accueil",
            "Générer une recette",
            "Liste de courses",
            "Historique de repas",
            "Tableau de bord"
        ])

    # Sections principales
    if mode == "Accueil":
        st.write("Bienvenue sur l'application de génération de recettes personnalisées !")
        st.image("https://via.placeholder.com/600x300", caption="Une alimentation équilibrée pour tous.")
        st.markdown("### Fonctionnalités :")
        st.write("- **Génération de recettes personnalisées**")
        st.write("- **Création automatique de listes de courses**")
        st.write("- **Suggestions basées sur vos repas précédents**")
        st.write("- **Suivi des objectifs nutritionnels**")

    elif mode == "Générer une recette":
        st.header("Générer une recette personnalisée")
        objectif = st.selectbox("Quel est votre objectif ?", [
            "Prise de masse",
            "Perte de poids",
            "Repas équilibré quotidien"
        ])
        ingredients_disponibles = st.text_area("Listez les ingrédients disponibles :", "ex: poulet, riz, brocoli")

        if st.button("Générer la recette"):
            st.success(f"Voici une recette pour {objectif} avec les ingrédients : {ingredients_disponibles}")
            st.write("\nRecette : Poulet grillé avec riz et brocoli sauté.")

    elif mode == "Liste de courses":
        st.header("Votre liste de courses")
        st.write("Générez une liste d'ingrédients automatiquement en fonction des recettes choisies.")
        if st.button("Créer ma liste de courses"):
            st.success("Voici votre liste de courses : \n- Poulet\n- Riz\n- Brocoli\n- Épices")

    elif mode == "Historique de repas":
        st.header("Historique de vos repas")
        st.write("Suivez vos repas pour des suggestions mieux adaptées.")
        st.text_area("Ajoutez les repas consommés aujourd'hui :", "ex: Petit-déjeuner: smoothie aux fruits")
        if st.button("Mettre à jour l'historique"):
            st.success("Historique mis à jour avec succès !")

    elif mode == "Tableau de bord":
        st.header("Tableau de bord")
        st.write("Visualisez vos progrès nutritionnels et vos objectifs.")
        st.metric(label="Calories consommées aujourd'hui", value="1800 kcal", delta="-200 kcal")
        st.metric(label="Protéines", value="120 g", delta="+20 g")
        st.metric(label="Lipides", value="50 g", delta="-10 g")

if __name__ == "__main__":
    main()
