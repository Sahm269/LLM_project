import streamlit as st

def info_perso():
    # Récupérer le gestionnaire de base de données
    db_manager = st.session_state.get("db_manager")

    if db_manager is None:
        st.error("Erreur : DBManager n'est pas initialisé.")
    else:
        # Récupérer les informations de l'utilisateur connecté
        user_id = st.session_state['user_id'] 
        query = f"SELECT * FROM utilisateurs WHERE id_utilisateur = {user_id}"
        user_info = db_manager.query(query)
        
        
        if not user_info:
            st.error("Utilisateur non trouvé.")
        else:
            user_info = user_info[0]  # Récupérer la première ligne (unique utilisateur)
            print(user_info)  # Récupérer et afficher les informations de l'utilisateur
            
            # Premier formulaire (Nom, Email, Mot de passe)
            col1, col2, col3 = st.columns(3)
            with col1:
                nom = st.text_input("Nom", user_info["login"])
            with col2:
                email = st.text_input("Email", user_info["email"])
            with col3:
                mot_de_passe = st.text_input("Mot de passe", value="********", type="password")

            # Deuxième formulaire (Objectifs nutritionnels, Poids, Taille)
            col1, col2, col3 = st.columns(3)
            with col1:
                
                objectifs_nutritionnels_val = user_info["objectifs_nutritionnels"] if user_info["objectifs_nutritionnels"] else "Vide"
                objectifs_nutritionnels = st.selectbox(
                    "Objectifs nutritionnels", 
                    ["Prise de masse", "Tonification", "Perdre du poids", "Vide"],
                    index=["Prise de masse", "Tonification", "Perdre du poids", "Vide"].index(objectifs_nutritionnels_val)
                )
            with col2:
                poids = st.number_input("Poids (kg)", value=user_info["poids"], step=1)
            with col3:
                taille = st.number_input("Taille (cm)", value=user_info["taille"], step=1)

            # Troisième formulaire (Régime particulier, Activité physique, Objectif calorique)
            col1, col2, col3 = st.columns(3)
            with col1:
                regime_particulier = st.text_area("Régime particulier", user_info["regime_particulier"])
            with col2:
                # Traitement de la valeur vide pour l'activité physique
                activite_physique_val = user_info["activite_physique"] if user_info["activite_physique"] else "Vide"
                activite_physique = st.selectbox(
                    "Activité physique",
                    ["Sédentaire", "Légère", "Modérée", "Intense", "Vide"],
                    index=["Sédentaire", "Légère", "Modérée", "Intense", "Vide"].index(activite_physique_val)
                )
            with col3:
                objectif_calorique = st.text_input("Objectif calorique", user_info["objectif_calorique"])

            # Bouton pour sauvegarder toutes les informations
            if st.button("Tout mettre à jour"):
                table_name = "utilisateurs"
                
                # Correction de la chaîne set_clause (ajout du guillemet manquant)
                set_clause = """login = %s, email = %s, mot_de_passe = %s, 
                                objectifs_nutritionnels = %s, poids = %s, taille = %s,
                                regime_particulier = %s, activite_physique = %s, objectif_calorique = %s"""
                condition = "id_utilisateur = %s"

                # Rassembler les paramètres à passer à la méthode
                params = (nom, email, mot_de_passe, objectifs_nutritionnels, poids, taille, 
                        regime_particulier, activite_physique, objectif_calorique, user_id)
                
                # Appel à la méthode update_data avec les bons paramètres
                db_manager.update_data(table_name, set_clause, condition, params)

                st.success("Informations mises à jour avec succès.")
