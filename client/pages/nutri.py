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
    update_conversation_title)

# Charger les variables d'environnement
# load_dotenv()
# api_key = os.getenv("api_key")
# mistral_client = Mistral(api_key=api_key)

st.markdown(
    """
    <style>
        .title-container {
            background-color: #6A5ACD;
            border-radius: 10px;
            color: white;
            text-align: center;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            font-family: New Icon;
            font-size: 25px;
        }

        .stbutton > button  {
        background:#D8BFD8;}

       
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="title-container">
        CHATBOT
    </div>
    """,
    unsafe_allow_html=True,
)



db_manager = st.session_state["db_manager"]
user_id = st.session_state["user_id"]




# Section pour afficher l'historique de la conversation
conversation_history = load_conversations(db_manager,user_id)

st.sidebar.title("Historique")
for index, conversation in enumerate(conversation_history):
    id_conversation = conversation['id_conversation']
    title = conversation['title']
    key = f"conversation_{id_conversation}_{index}"  # Clé unique pour chaque bouton
    
    # Vérifier si cette conversation est active
    if "id_conversation" in st.session_state and st.session_state.id_conversation == id_conversation:
        # Bouton désactivé pour la conversation active
        st.sidebar.button(f"🟢 {title}", key=key, disabled=True)
    else:
        # Bouton actif pour sélectionner une autre conversation
        if st.sidebar.button(title, key=key):
            # Charger la conversation sélectionnée
            st.session_state.id_conversation = id_conversation
            st.session_state.messages = load_messages(db_manager, id_conversation)
            update_conversation(db_manager,id_conversation=st.session_state.id_conversation,id_utilisateur=user_id)
            st.rerun()
            
# Ajouter un bouton pour démarrer une nouvelle conversation
if st.sidebar.button("➕ Nouveau chat"):
    # Créer une nouvelle conversation
    title = "Nouvelle conversation"
    new_conversation_id = create_conversation(db_manager, title, user_id)

    # Initialiser la session avec cette nouvelle conversation
    st.session_state.id_conversation = new_conversation_id
    st.session_state.messages = []  # Réinitialiser les messages

    # Redémarrer l'application pour afficher la nouvelle conversation
    st.rerun()


# Historique de la conversation
if "id_conversation" not in st.session_state:
    st.session_state.id_conversation = None

# Affichage des messages précédents
if st.session_state.id_conversation:
    st.session_state.messages = load_messages(db_manager,st.session_state.id_conversation)

if "mistral_model" not in st.session_state:
    st.session_state["mistral_model"] = "mistral-large-latest"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):  # Utilisez votre avatar utilisateur
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="client/assets/avatar_bot_big.jpg"):  # Avatar personnalisé pour l'assistant
            st.markdown(message["content"])

# Initialisation de Mistral
mistral = MistralAPI(model=st.session_state["mistral_model"])

if prompt := st.chat_input("Dîtes quelque-chose"):
    retries = 0
    max_retries = 3
    while retries < max_retries:
        try:
            title = mistral.auto_wrap(prompt) # Générer un titre basé sur le premier messag
        except Exception as e:
            # Vérifier explicitement si l'erreur est une 429 (rate limit exceeded)
            if hasattr(e, "status_code") and e.status_code == 429:
                retries += 1
                wait_time = 2 ** retries  # Temps d'attente exponentiel
                st.warning(f"Limite de requêtes atteinte (429). Nouvel essai dans {wait_time} secondes...")
                time.sleep(wait_time)
            else:
                # Gérer d'autres types d'erreurs
                st.error(f"Erreur : Impossible de traiter votre demande (déetails : {str(e)})")
                st.stop()
        if title is not None:
            break
    # Si tous les retries échouent, retourner un message d'erreur
    if title is None:
        st.error("Impossible d'obtenir une réponse. Limite de requêtes atteinte après plusieurs tentatives.")
        st.stop()
    
    if st.session_state.id_conversation is None:
        st.session_state.id_conversation = create_conversation(db_manager, title, user_id)
    else:
        # Vérifier si le titre est encore "Nouvelle conversation" et le mettre à jour si nécessaire
        current_title = get_conversation_title(db_manager, st.session_state.id_conversation)
        if current_title == "Nouvelle conversation":
            new_title = title
            update_conversation_title(db_manager, st.session_state.id_conversation, new_title)

    # Ajouter le message de l'utilisateur à la session et à la base de données
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(db_manager=db_manager, id_conversation=st.session_state.id_conversation, role="user", content=prompt)


    # Afficher le message de l'utilisateur dans l'interface Streamlit
    with st.chat_message("user"):
        st.markdown(prompt)

    ###################
    #### Guardrail ####
    ###################

    try:
        guardrail = Guardrail()
    except Exception as e:
        st.error(f"Guardrail introuvable. Veuillez relancer le conteneur pour recréer le guardrail. Détails : {e}")
        st.stop()
    # is_supported = asyncio.run(guardrail.analyze_language(prompt))
    # if not is_supported:
    #     st.warning("To use our bot in a safe manner, you must do the conversation in either english, french, german or spanish. If necessary you may use an online translator.")
    #     st.stop()
    is_safe = guardrail.analyze_query(prompt)
    if not is_safe:
        st.warning("Le prompt semble violer nos considérations éthiques. Nous vous invitons à poser une autre question.")
        st.stop()
    ###################

    with st.chat_message("assistant", avatar = "client/assets/avatar_bot_big.jpg"):
        retries = 0
        max_retries = 3
        while retries < max_retries:
            response = ""
            response_placeholder = st.empty()
            try:
                stream_response = mistral.stream(st.session_state.messages) # Utiliser le début du message comme titr
                # Traiter la réponse en streaming
                for chunk in stream_response:
                    response += chunk.data.choices[0].delta.content
                    response_placeholder.markdown(response)
                    time.sleep(0.03)  # Petit délai pour simuler le flux en temps réel
            except Exception as e:
                if hasattr(e, "status_code") and e.status_code == 429:
                    # Gestion explicite de l'erreur 429 (Rate Limit Exceeded)
                    retries += 1
                    wait_time = 2 ** retries  # Délai exponentiel : 2, 4, 8 secondes
                    st.warning(f"Limite de requêtes atteinte (429). Nouvel essai dans {wait_time} secondes...")
                    time.sleep(wait_time)
                else:
                    # Gestion d'autres types d'erreurs
                    st.error(f"Erreur : Impossible de traiter votre demande (détails : {str(e)})")
                    response_placeholder.markdown("Erreur lors de la génération de la réponse.")
                    st.stop()
            if stream_response is not None:
                break  # Si le streaming réussit, on sort de la boucle
        # Si toutes les tentatives échouent, message d'erreur final
        if retries >= max_retries:
            st.error("Impossible d'obtenir une réponse. Limite de requêtes atteinte après plusieurs tentatives.")
            response = "Erreur : Limite de requêtes atteinte après plusieurs tentatives."
        st.session_state.messages.append({"role": "assistant", "content": response})


        save_message(db_manager,id_conversation=st.session_state.id_conversation, role="assistant", content=response)





