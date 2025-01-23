import streamlit as st
import time



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


# CSS Styling
st.markdown("""
    <style>
    .features-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 20px;
    }
    .feature-card {
        background: linear-gradient(135deg, #FFDDC1, #FF9A76);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease;
    }
    .feature-card:hover {
        transform: scale(1.05);
    }
    .feature-card img {
        width: 60px;
        height: 60px;
        margin-bottom: 15px;
    }
    .feature-card h3 {
        margin-bottom: 10px;
        font-size: 1.3em;
        color: #fff;
    }
    .feature-card p {
        font-size: 1em;
        color: #fefefe;
    }
    </style>
""", unsafe_allow_html=True)

# HTML Content
st.markdown("""
    <div class="features-container">
        <div class="feature-card">
            <img src="https://via.placeholder.com/60" alt="Recipe Icon" class="feature-icon">
            <h3>Génération de recettes personnalisées</h3>
            <p>Adaptées à vos objectifs spécifiques.</p>
        </div>
        <div class="feature-card">
            <img src="https://via.placeholder.com/60" alt="Shopping List Icon" class="feature-icon">
            <h3>Création automatique de listes de courses</h3>
            <p>Simplifiez vos achats.</p>
        </div>
        <div class="feature-card">
            <img src="https://via.placeholder.com/60" alt="Suggestions Icon" class="feature-icon">
            <h3>Suggestions basées sur vos repas précédents</h3>
            <p>Pour une alimentation équilibrée.</p>
        </div>
        <div class="feature-card">
            <img src="https://via.placeholder.com/60" alt="Dashboard Icon" class="feature-icon">
            <h3>Tableau de bord interactif</h3>
            <p>Suivez vos progrès et métriques en temps réel.</p>
        </div>
        <div class="feature-card">
            <img src="https://via.placeholder.com/60" alt="Security Icon" class="feature-icon">
            <h3>Sécurité renforcée</h3>
            <p>Protégez vos données et interactions avec l'application.</p>
        </div>
    </div>
""", unsafe_allow_html=True)



# Membres de l'équipe
team_members = [
    {"name": "Souraya", "role": "Chef de projet et Data Scientist", "photo": "https://via.placeholder.com/300"},
    {"name": "Membre 2", "role": "Expert en Machine Learning", "photo": "https://via.placeholder.com/300"},
    {"name": "Membre 3", "role": "Développeur Front-End", "photo": "https://via.placeholder.com/300"},
    {"name": "Membre 4", "role": "Spécialiste en RAG", "photo": "https://via.placeholder.com/300"},
    {"name": "Membre 5", "role": "Architecte de Base de Données", "photo": "https://via.placeholder.com/300"},
    {"name": "Membre 6", "role": "Designer UX/UI", "photo": "https://via.placeholder.com/300"},
]

# Initialiser l'index du carrousel
if "carousel_index" not in st.session_state:
    st.session_state["carousel_index"] = 0

# Fonction pour avancer ou reculer dans le carrousel
def update_index(step: int):
    st.session_state["carousel_index"] = (st.session_state["carousel_index"] + step) % len(team_members)

# Section avec un espace en haut pour aérer visuellement
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <h2 style="text-align: center; color: #6A0DAD; font-family: 'Arial', sans-serif;'>Rencontrez l'équipe NutriGenie</h2>
    <p style="text-align: center; color: #999; font-size: 1.1em;'>Nos experts dévoués qui rendent l'impossible possible</p>
    """,
    unsafe_allow_html=True,
)

# Navigation du carrousel
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("⬅️", key="prev"):
        update_index(-1)

with col3:
    if st.button("➡️", key="next"):
        update_index(1)

# Calcul des membres affichés (3 en même temps)
start_idx = st.session_state["carousel_index"]
visible_members = [
    team_members[(start_idx + i) % len(team_members)] for i in range(3)
]

# Affichage horizontal garanti avec `st.columns`
cols = st.columns(3)  # Divise en trois colonnes pour alignement horizontal

for col, member in zip(cols, visible_members):
    with col:
        st.markdown(
            f"""
            <div style="
                text-align: center; 
                background: linear-gradient(135deg, #6A0DAD, #38006B); 
                border-radius: 12px; 
                padding: 20px; 
                color: white; 
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                <img src="{member['photo']}" alt="Photo de {member['name']}" style="
                    border-radius: 50%; 
                    width: 100px; 
                    height: 100px; 
                    object-fit: cover; 
                    border: 3px solid #fff; 
                    margin-bottom: 15px;">
                <h3 style="margin: 10px 0 5px; font-size: 1.2em;">{member['name']}</h3>
                <p style="font-size: 0.9em; color: #dcdcdc;">{member['role']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
