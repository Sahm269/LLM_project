import streamlit as st



# Style de la page
st.markdown(
    """
    <style>
        .hero {
            background-color: #FFFAF0;
            padding: 50px;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        .hero h1 {
            color: #FF9900;
            font-size: 3em;
            text-align: center;
            margin-bottom: 20px;
        }
        .hero p {
            color: #444444;
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 40px;
        }
        .team-section {
            margin-top: 50px;
        }
        .team-section h2 {
            color: #FF6600;
            text-align: center;
            margin-bottom: 30px;
        }
        .team-member {
            text-align: center;
            margin-bottom: 20px;
        }
        .team-member img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin-bottom: 10px;
        }
        .team-member h4 {
            color: #333333;
            margin-bottom: 5px;
        }
        .team-member p {
            color: #777777;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Section Hero
st.markdown(
    """
    <div class="hero">
        <h1>Bienvenue sur NutriGenie 🍴</h1>
        <p>Découvrez une application magique qui personnalise vos recettes selon vos besoins nutritionnels et vos objectifs !</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Présentation des fonctionnalités
st.header("Fonctionnalités de NutriGenie")
st.write("- **Génération de recettes personnalisées** : adaptées à vos objectifs spécifiques.")
st.write("- **Création automatique de listes de courses** : simplifiez vos achats.")
st.write("- **Suggestions basées sur vos repas précédents** : pour une alimentation équilibrée.")
st.write("- **Tableau de bord interactif** : suivez vos progrès et métriques en temps réel.")
st.write("- **Sécurité renforcée** : protégez vos données et interactions avec l'application.")

# Présentation de l'équipe
st.markdown(
    """
    <div class="team-section">
        <h2>L'équipe NutriGenie</h2>
        <div class="team-member">
            <img src="https://via.placeholder.com/120" alt="Photo membre 1">
            <h4>Souraya</h4>
            <p>Chef de projet et Data Scientist</p>
        </div>
        <div class="team-member">
            <img src="https://via.placeholder.com/120" alt="Photo membre 2">
            <h4>Membre 2</h4>
            <p>Expert en Machine Learning</p>
        </div>
        <div class="team-member">
            <img src="https://via.placeholder.com/120" alt="Photo membre 3">
            <h4>Membre 3</h4>
            <p>Développeur Front-End</p>
        </div>
        <div class="team-member">
            <img src="https://via.placeholder.com/120" alt="Photo membre 4">
            <h4>Membre 4</h4>
            <p>Spécialiste en RAG</p>
        </div>
        <div class="team-member">
            <img src="https://via.placeholder.com/120" alt="Photo membre 5">
            <h4>Membre 5</h4>
            <p>Architecte de Base de Données</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
