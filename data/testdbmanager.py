from dbmanager import DBManager

# Création d'une instance de DBManager
db_manager = DBManager(db_name="recettes_personnalisees.db", schema_file="schema.json")

# Insérer des données depuis un dictionnaire
data = [
    {"login": "utilisateur1", "mot_de_passe": "password123", "nom": "Souraya", "email": "souraya@example.com"},
    {"login": "utilisateur2", "mot_de_passe": "password456", "nom": "Ali", "email": "ali@example.com"}
]
db_manager.insert_data_from_dict("utilisateurs", data)

# Insérer des données depuis un fichier CSV
#db_manager.insert_data_from_csv("recettes", "recettes.csv")

# Récupérer toutes les données de la table "utilisateurs"
utilisateurs = db_manager.fetch_all("utilisateurs")
print(utilisateurs)

# Mettre à jour des données
db_manager.update_data("utilisateurs", "mot_de_passe = ?", "login = ?", ("newpassword", "utilisateur1"))

# Fermer la connexion
db_manager.close_connection()
