import streamlit as st
import os

st.markdown("""
    <style>
        body, .stApp {
            background: linear-gradient(to right, #cae7d4, #a8d8b9);
        }

        .main {
            background: linear-gradient(to right, #cae7d4, #a8d8b9);
            background-size: 400% 400%;
            animation: gradientAnimation 10s ease infinite;
        }

        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .presentation {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .left-col, .right-col {
            border-radius: 12px;
            overflow: hidden;
        }

        .stButton>button {
            background-color: #a8d8b9;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }

        body {
            font-family: 'Poppins', sans-serif;
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
        }

        .presentation-text {
            font-size: 1.3rem;
            color: #4e7a63;
            text-align: center;
            font-style: italic;
            animation: fadeIn 3s ease-out;
        }

        .feature-icon {
            font-size: 2rem;
            margin-right: 1rem;
        }

        .features {
            background-color: #e2f4f1;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-out;
            transition: transform 0.3s ease;
            margin-bottom: 1rem;
        }

        .features:hover {
            transform: translateY(-5px);
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
        }

        .team-name-role {
            color: #2a4b47;
            font-size: 1.1rem;
            margin-top: 0.5rem;
            font-weight: 500;
            font-style: italic;
            text-align: center;
        }

        .team-name {
            color: #2a4b47;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
        }

    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <h2 class="welcome-title">
        Bienvenue sur NutriGénie <span class="user-name">{st.session_state['user']}</span> 🍽️!
    </h2>
""", unsafe_allow_html=True)

st.markdown("""
    <br>
    <div class="presentation-text">
        " Laissez-nous vous guider à travers une expérience culinaire sur-mesure. Découvrez des recettes adaptées à vos préférences et suivez vos habitudes alimentaires en toute simplicité. "
    </div>
    <br>
""", unsafe_allow_html=True)

logo_path = "assets/logo.png"

col1, col_gap, col2 = st.columns([6, 1, 2])

with col1:
    st.markdown("""
        <h3 style="color:#2a4b47; text-align:center;">Fonctionnalités principales de l'application :</h3>
    """, unsafe_allow_html=True)

    # Fonctionnalités
    st.markdown("""
        <div class="features">
            <div style="display: flex; align-items: center;">
                <span class="feature-icon">🍽️</span>
                <h3><strong>Génération de recettes personnalisées</strong></h3>
            </div>
            <p>Créez des recettes adaptées à vos préférences et vos besoins alimentaires. Nous générons des suggestions personnalisées pour chaque utilisateur.</p>
        </div>
        <div class="features">
            <div style="display: flex; align-items: center;">
                <span class="feature-icon">📝</span>
                <h3><strong>Suivi des repas</strong></h3>
            </div>
            <p>Consultez l'historique de vos repas consommés et suivez vos habitudes alimentaires au fil du temps.</p>
        </div>
        <div class="features">
            <div style="display: flex; align-items: center;">
                <span class="feature-icon">🛒</span>
                <h3><strong>Liste de courses</strong></h3>
            </div>
            <p>Générez automatiquement des listes de courses basées sur les recettes que vous avez choisies. Ne manquez plus d'ingrédients !</p>
        </div>
        <div class="features">
            <div style="display: flex; align-items: center;">
                <span class="feature-icon">🍴</span>
                <h3><strong>Suggestions de repas</strong></h3>
            </div>
            <p>Obtenez des suggestions de repas en fonction de vos goûts et de vos besoins nutritionnels.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True, caption=None) 

# Présentation des membres de l'équipe
st.markdown("<hr>", unsafe_allow_html=True)  # Ajoute une ligne de séparation

st.subheader("Rencontrez notre équipe 👩‍🍳👨‍🍳")

# Définition des 5 membres
membres = [
    {"nom": "Souraya", "role": "Chef de projet", "photo": "assets/membre1.jpg", "emoji_role": "👩‍💻"},
    {"nom": "Bertrand", "role": "Développeur Backend", "photo": "assets/membre2.jpg", "emoji_role": "💻"},
    {"nom": "Cyril", "role": "Développeur Backend", "photo": "assets/membre3.jpg", "emoji_role": "🖥️"},
    {"nom": "Linh Nhi", "role": "Développeur Frontend", "photo": "assets/membre4.jpg", "emoji_role": "🎨"},
    {"nom": "Daniella", "role": "Développeur Frontend", "photo": "assets/membre5.jpg", "emoji_role": "🎨"}
]

# Création des colonnes pour chaque membre
cols = st.columns(5)

for i, membre in enumerate(membres):
    with cols[i]:
        st.image(membre["photo"], use_container_width=True, caption=None)
        st.markdown(f"""
            <div class="team-member">
                <div class="team-name">{membre['nom']}</div>
                <div class="team-name-role">{membre['emoji_role']} {membre['role']}</div>
            </div>
        """, unsafe_allow_html=True)
