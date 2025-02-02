import streamlit as st
import os
import time
from server.mistral.mistralapi import MistralAPI
from server.security.prompt_guard import Guardrail
import asyncio
from typing import List, Dict
from server.db.dbmanager import (
    load_conversations,
    load_messages, 
    update_conversation,
    create_conversation,
    save_message,
    get_conversation_title,
    update_conversation_title,
    delete_conversation  
)

# 🔹 Chargement des variables de session pour éviter les rechargements inutiles
if "id_conversation" not in st.session_state:
    st.session_state.id_conversation = None

if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = "mistral-large-latest"

if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialise l'historique des messages

# 🔹 Initialisation unique de MistralAPI
if "mistral_instance" not in st.session_state:
    print("🔄 Initialisation de MistralAPI...")
    st.session_state.mistral_instance = MistralAPI(model=st.session_state["mistral_model"])
    print("✅ MistralAPI initialisé avec succès.")

mistral = st.session_state.mistral_instance  # Récupérer l'instance stockée

# 🔹 Initialisation de la sécurité (Guardrail)
try:
    guardrail = Guardrail()
except Exception as e:
    st.error(f"❌ Guardrail introuvable. Veuillez relancer le conteneur. Détails : {e}")
    st.stop()

# 🔹 Chargement de la base de données
db_manager = st.session_state["db_manager"]
user_id = st.session_state["user_id"]

# 🔹 Sidebar : Bouton "➕ Nouveau chat" en haut
st.sidebar.title("🗂️ Historique")
if st.sidebar.button("➕ Nouveau chat"):
    title = "Nouvelle conversation"
    new_conversation_id = create_conversation(db_manager, title, user_id)
    st.session_state.id_conversation = new_conversation_id
    st.session_state.messages = []  
    st.rerun()

# 🔹 Charger l'historique des conversations
conversation_history = load_conversations(db_manager, user_id) or []

# 🔹 Sidebar : Affichage de l'historique des conversations avec bouton de suppression
for index, conversation in enumerate(conversation_history):
    id_conversation = conversation['id_conversation']
    title = conversation['title']
    key = f"conversation_{id_conversation}_{index}"  # Clé unique

    col1, col2 = st.sidebar.columns([0.8, 0.2])  # 🔹 Disposition pour aligner le bouton de suppression

    with col1:
        if "id_conversation" in st.session_state and st.session_state.id_conversation == id_conversation:
            st.button(f"🟢 {title}", key=key, disabled=True)
        else:
            if st.button(title, key=key):
                st.session_state.id_conversation = id_conversation
                st.session_state.messages = load_messages(db_manager, id_conversation)
                update_conversation(db_manager, id_conversation=st.session_state.id_conversation, id_utilisateur=user_id)
                st.rerun()

    with col2:
        if st.button("🗑️", key=f"delete_{id_conversation}"):  # 🔥 Bouton de suppression
            delete_conversation(db_manager, id_conversation)
            st.rerun()  # Rafraîchir après suppression

# 🔹 Affichage des messages précédents dans l'interface
for message in st.session_state.messages:
    timestamp = message.get("timestamp", "Non spécifié")
    latency = message.get("temps_traitement", None)
    latency_text = f"⏳ {latency} sec" if latency is not None else ""

    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
            st.caption(f"📅 {timestamp} {latency_text}")

    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="client/assets/avatar_bot_big.jpg"):
            st.markdown(message["content"])
            st.caption(f"📅 {timestamp} {latency_text}")  # 🔹 Ajout de l'heure et de la latence


# 🔹 Interface utilisateur - Zone d'entrée utilisateur
if prompt := st.chat_input("Dîtes quelque-chose"):

    # 🔸 Vérifier la sécurité du message
    is_safe = guardrail.analyze_query(prompt)

    # 🔸 Afficher immédiatement le message de l'utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)

    # 🔸 Ajouter le message à l'historique et l'enregistrer dans la base de données
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(db_manager, st.session_state.id_conversation, role="user", content=prompt, temps_traitement=None)

    # 🔸 Si le message est interdit, afficher l'alerte mais NE PAS l'envoyer à Mistral
    if not is_safe:
        st.warning("⚠️ Votre message ne respecte pas nos consignes.")
        st.stop()  # Arrêter l'exécution ici pour ne PAS envoyer à Mistral

    retries = 0
    max_retries = 3

    # 🔹 Générer une réponse avec Mistral et RAG
    with st.chat_message("assistant", avatar="client/assets/avatar_bot_big.jpg"):
        retries = 0
        max_retries = 3
        while retries < max_retries:
            response = ""
            response_placeholder = st.empty()
            try:
                start_time = time.time()  # 🔹 Début du chronomètre

                print("🔄 Génération de réponse en cours...")
                stream_response = mistral.stream(st.session_state.messages, temperature=0.5)

                for chunk in stream_response:
                    response += chunk.data.choices[0].delta.content
                    response_placeholder.markdown(response)
                    time.sleep(0.03)

                end_time = time.time()  # 🔹 Fin du chronomètre
                latency = round(end_time - start_time, 2)  # 🔹 Calcul de la latence

                print(f"✅ Réponse générée en {latency} secondes.")
            except Exception as e:
                if hasattr(e, "status_code") and e.status_code == 429:
                    retries += 1
                    wait_time = 2 ** retries  
                    stream_response = None
                    print(f"⚠️ Rate limit atteint. Nouvel essai dans {wait_time} secondes...")
                    time.sleep(wait_time)
                else:
                    st.error(f"❌ Erreur : Impossible de traiter votre demande. Détails : {str(e)}")
                    response_placeholder.markdown("❌ Erreur lors de la génération de la réponse.")
                    st.stop()

            if stream_response is not None:
                break  

        if retries >= max_retries:
            st.error("❌ Impossible d'obtenir une réponse après plusieurs tentatives.")
            response = "❌ Erreur : Limite de requêtes atteinte."

        # 🔹 Enregistrer la réponse de l'assistant
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message(db_manager, st.session_state.id_conversation, role="assistant", content=response, temps_traitement=latency)
