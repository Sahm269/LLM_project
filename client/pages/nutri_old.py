import streamlit as st
import time
from server.mistral.mistralapi import MistralAPI
from server.security.prompt_guard import Guardrail
from projects.LLM_project.server.db.db_sqlite import (
    load_conversations,
    load_messages,
    update_conversation,
    create_conversation,
    save_message,
)


def nutri_page():
    # Interface Streamlit
    # st.set_page_config(page_title="Nutrigénie", layout="wide")
    # Section pour afficher l'historique de la conversation
    conversation_history = load_conversations()
    # st.sidebar.title("Navigation")
    st.sidebar.title("Historique")

    for conversation_id, _, title in conversation_history:
        if (
            "conversation_id" in st.session_state
            and st.session_state.conversation_id == conversation_id
        ):
            # Bouton désactivé pour la conversation active
            st.sidebar.button(
                f"🟢 {title}", key=f"conversation_{conversation_id}", disabled=True
            )
        else:
            # Bouton actif pour les autres conversations
            if st.sidebar.button(title, key=f"conversation_{conversation_id}"):
                # Charger la conversation sélectionnée
                st.session_state.conversation_id = conversation_id
                st.session_state.messages = load_messages(conversation_id)
                update_conversation(conversation_id=st.session_state.conversation_id)
                st.rerun()

    st.title("Parlez au Nutrigénie")
    # Historique de la conversation
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    # Affichage des messages précédents
    if st.session_state.conversation_id:
        st.session_state.messages = load_messages(st.session_state.conversation_id)

    if "mistral_model" not in st.session_state:
        st.session_state["mistral_model"] = "mistral-large-latest"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):  # Utilisez votre avatar utilisateur
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message(
                "assistant", avatar="client/assets/avatar_bot_big.jpg"
            ):  # Avatar personnalisé pour l'assistant
                st.markdown(message["content"])

    # Initialisation de Mistral
    mistral = MistralAPI(model=st.session_state["mistral_model"])
    if prompt := st.chat_input("Dîtes quelque-chose"):
        if st.session_state.conversation_id is None:
            retries = 0
            max_retries = 3
            while retries < max_retries:
                try:
                    title = mistral.auto_wrap(
                        prompt
                    )  # Utiliser le début du message comme titre
                except Exception as e:
                    # Vérifier explicitement si l'erreur est une 429 (rate limit exceeded)
                    if hasattr(e, "status_code") and e.status_code == 429:
                        retries += 1
                        wait_time = 2 ** retries  # Temps d'attente exponentiel
                        st.warning(
                            f"Limite de requêtes atteinte (429). Nouvel essai dans {wait_time} secondes..."
                        )
                        time.sleep(wait_time)
                    else:
                        # Gérer d'autres types d'erreurs
                        st.error(
                            f"Erreur : Impossible de traiter votre demande (déetails : {str(e)})"
                        )
                        st.stop()
                if title is not None:
                    break
            # Si tous les retries échouent, retourner un message d'erreur
            if title is None:
                st.error(
                    "Impossible d'obtenir une réponse. Limite de requêtes atteinte après plusieurs tentatives."
                )
                st.stop()

            st.session_state.conversation_id = create_conversation(title=title)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(
            conversation_id=st.session_state.conversation_id,
            role="user",
            content=prompt,
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        ###################
        #### Guardrail ####
        ###################

        try:
            guardrail = Guardrail()
        except Exception as e:
            st.error(
                f"Guardrail introuvable. Veuillez relancer le conteneur pour recréer le guardrail. Détails : {e}"
            )
            st.stop()
        # is_supported = await guardrail.analyze_language(prompt)
        # if not is_supported:
        #     st.warning("To use our bot in a safe manner, you must do the conversation in either english, french, german or spanish. If necessary you may use an online translator.")
        #     st.stop()
        is_safe = guardrail.analyze_query(prompt)
        if not is_safe:
            st.warning(
                "Le prompt semble violer nos considérations éthiques. Nous vous invitons à poser une autre question."
            )
            st.stop()

        ####################
        ###### PROMPT ######
        ####################

        with st.chat_message("assistant", avatar="client/assets/avatar_bot_big.jpg"):
            retries = 0
            max_retries = 3
            while retries < max_retries:
                response = ""
                response_placeholder = st.empty()
                try:
                    stream_response = mistral.stream(
                        st.session_state.messages
                    )  # Utiliser le début du message comme titr
                    # Traiter la réponse en streaming
                    for chunk in stream_response:
                        response += chunk.data.choices[0].delta.content
                        response_placeholder.markdown(response)
                        time.sleep(
                            0.03
                        )  # Petit délai pour simuler le flux en temps réel
                except Exception as e:
                    if hasattr(e, "status_code") and e.status_code == 429:
                        # Gestion explicite de l'erreur 429 (Rate Limit Exceeded)
                        retries += 1
                        wait_time = 2 ** retries  # Délai exponentiel : 2, 4, 8 secondes
                        st.warning(
                            f"Limite de requêtes atteinte (429). Nouvel essai dans {wait_time} secondes..."
                        )
                        time.sleep(wait_time)
                    else:
                        # Gestion d'autres types d'erreurs
                        st.error(
                            f"Erreur : Impossible de traiter votre demande (détails : {str(e)})"
                        )
                        response_placeholder.markdown(
                            "Erreur lors de la génération de la réponse."
                        )
                        st.stop()
                if stream_response is not None:
                    break  # Si le streaming réussit, on sort de la boucle
            # Si toutes les tentatives échouent, message d'erreur final
            if retries >= max_retries:
                st.error(
                    "Impossible d'obtenir une réponse. Limite de requêtes atteinte après plusieurs tentatives."
                )
                response = (
                    "Erreur : Limite de requêtes atteinte après plusieurs tentatives."
                )
            st.session_state.messages.append({"role": "assistant", "content": response})
            save_message(
                conversation_id=st.session_state.conversation_id,
                role="assistant",
                content=response,
            )
