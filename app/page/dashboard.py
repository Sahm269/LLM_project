import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Fonction pour obtenir la connexion à la base de données
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Connexion à la base de données pour récupérer le nombre total de recettes
def get_recipes_count():
    conn = get_db_connection()
    if conn is None:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recettes")
        result = cursor.fetchone()
        return result[0]  # Le nombre total de recettes
    except Exception as e:
        st.error(f"Erreur lors de la récupération du nombre de recettes : {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

# Fonction pour récupérer la latence moyenne des messages
def get_average_latency():
    conn = get_db_connection()
    if conn is None:
        return 0.0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(temps_traitement) FROM messages WHERE temps_traitement IS NOT NULL")
        result = cursor.fetchone()
        return round(result[0], 2) if result[0] is not None else 0.0
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données pour la latence : {e}")
        return 0.0
    finally:
        cursor.close()
        conn.close()

# Récupérer les données pour afficher sur le dashboard
total_recipes = get_recipes_count()
average_latency = get_average_latency()

# Affichage de la page dashboard avec Streamlit
st.markdown(
    """
    <div class="title-container">
         DASHBOARD
    </div>
    """,
    unsafe_allow_html=True,
)

# Ajouter le CSS pour les cards avec animations et un design moderne
st.markdown("""
    <style>
        .title-container {
            background-color: #FF9A76;
            border-radius: 10px;
            color: white;
            text-align: center;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            font-family: New Icon;
            font-size: 30px;
        }

        /* Style pour les cards */
        .card {
            border-radius: 15px;
            padding: 20px;
            background: linear-gradient(to top, #cae7d4, #a7d7b8);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
            animation: fadeInUp 0.5s ease-out;
        }

        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
        }

        @keyframes fadeInUp {
            0% {
                transform: translateY(20px);
                opacity: 0;
            }
            100% {
                transform: translateY(0);
                opacity: 1;
            }
        }

        .card-title {
            font-size: 1.3em;
            color: #2d3e50;
            margin-bottom: 15px;
            font-weight: bold;
            font-family: New Icon;
        }

        .card-value {
            font-size: 30px;
            color: #0099cc;
            font-weight: bold;
        }

        /* Add smooth transition for the hover effect */
        .card .card-title, .card .card-value {
            transition: color 0.3s ease;
        }

        .card:hover {
            color: #FF9A76;
        }
        .card:hover .card-value {
            color: #0086b3;
        }
    </style>
""", unsafe_allow_html=True)

# Créer des colonnes pour disposer les cards
col1, col2, col3 = st.columns(3)

# Card 1
with col1:
    st.markdown(f"""
        <div class="card">
            <div class="card-title">🍲 Nombre total de recettes</div>
            <div class="card-value">{total_recipes}</div>
        </div>
    """, unsafe_allow_html=True)

# Card 2
with col2:
    st.markdown("""
        <div class="card">
            <div class="card-title">🍽️ Repas consommés</div>
            <div class="card-value small">2450</div>
        </div>
    """, unsafe_allow_html=True)

# Card 3
with col3:
    st.markdown("""
        <div class="card">
            <div class="card-title">🥗 Recettes par type</div>
            <div class="card-value">30%</div>
        </div>
    """, unsafe_allow_html=True)

# Créer une nouvelle ligne de cards
col4, col5, col6 = st.columns(3)

# Card 4
with col4:
    st.markdown(f"""
        <div class="card">
            <div class="card-title">⏱️ Latence moyenne</div>
            <div class="card-value">{average_latency}s</div>
        </div>
    """, unsafe_allow_html=True)

# Card 5
with col5:
    st.markdown("""
        <div class="card">
            <div class="card-title">💸 Coût total des requêtes</div>
            <div class="card-value">$150.45</div>
        </div>
    """, unsafe_allow_html=True)

# Card 6
with col6:
    st.markdown("""
        <div class="card">
            <div class="card-title">🌱 Impact écologique estimé</div>
            <div class="card-value">500kg CO2</div>
        </div>
    """, unsafe_allow_html=True)
