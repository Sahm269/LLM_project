import streamlit as st
import psycopg2
from psycopg2 import extras
from datetime import datetime
import logging
import json
import pandas as pd
from typing import List, Dict, Tuple
import os
import sys 

# Configuration du logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

sys.stdout.reconfigure(encoding='utf-8')

# Configuration de la base de données
db_config = {
    "database": st.secrets["DB_NAME"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"]
}

######################### CLASSES #########################

class DBManager:
    def __init__(self, db_config: Dict, schema_file: str):
        """
        Initialise la connexion à la base PostgreSQL et charge le schéma.
        
        :param db_config: Dictionnaire avec les informations de connexion (host, database, user, password).
        :param schema_file: Chemin vers le fichier JSON contenant le schéma de la base.
        """

        self.db_config = db_config
        self.schema_file = schema_file
        self.connection = None
        self.cursor = None
        self._load_schema()
        self._connect_to_database()
        self._create_database()
        self.cursor.execute("SET NAMES 'UTF8'")

        

    def _load_schema(self):
        """Charge le schéma de base de données depuis un fichier JSON."""
        if not os.path.exists(self.schema_file):
            raise FileNotFoundError(f"Fichier non trouvé : {self.schema_file}")
        
        with open(self.schema_file, "r", encoding="utf-8") as file:
            self.schema = json.load(file)

    def _connect_to_database(self):
        """Établit une connexion avec la base PostgreSQL."""
        try:
            self.connection = psycopg2.connect(**self.db_config, cursor_factory=extras.RealDictCursor)
            self.cursor = self.connection.cursor()
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return

    def _create_database(self):
        """Crée les tables définies dans le schéma JSON."""
        for table_name, table_info in self.schema['tables'].items():
            create_table_query = self._generate_create_table_query(table_name, table_info['columns'])
            try:
                self.cursor.execute(create_table_query)
            except psycopg2.Error as err:
                logger.error(f"Erreur de connexion : {err}")
                return
            finally:
                self.connection.commit()

    def _generate_create_table_query(self, table_name: str, columns: List[Dict]) -> str:
        """Génère une requête SQL pour créer une table en fonction du schéma."""
        column_definitions = []
        for column in columns:
            column_definition = f"{column['name']} {column['type']}"
            if 'constraints' in column and column['constraints']:
                column_definition += " " + " ".join(column['constraints'])
            column_definitions.append(column_definition)
        columns_str = ", ".join(column_definitions)
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"

    def insert_data_from_dict(self, table_name: str, data: List[Dict], id_column: str) -> List[int]:
        """Insère des données dans une table à partir d'une liste de dictionnaires et retourne les IDs insérés.
        
        table_name : str : nom de la table
        data : List[Dict] : données à insérer
        id_column : str : nom de la colonne d'ID à retourner
        """
        columns = ", ".join(data[0].keys())
        placeholders = ", ".join(['%s' for _ in data[0].keys()])
        
        # Requête pour insérer les données et retourner l'ID dynamique
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING {id_column}"  
        
        ids = []  # Liste pour stocker les IDs retournés
        try:
            for row in data:
                self.cursor.execute(query, tuple(row.values()))
                inserted_id = self.cursor.fetchone()[0]  
                ids.append(inserted_id)
            return ids
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
        finally:
            self.connection.commit()

        



    def insert_data_from_csv(self, table_name: str, csv_file: str) -> None:
        """Insère des données dans une table à partir d'un fichier CSV."""
        df = pd.read_csv(csv_file)
        columns = df.columns.tolist()
        placeholders = ", ".join(['%s' for _ in columns])
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            for row in df.itertuples(index=False, name=None):
                self.cursor.execute(query, row)
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
        finally:
            self.connection.commit()

    def fetch_all(self, table_name: str) -> List[Tuple]:
        """Récupère toutes les données d'une table."""
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
    
    
    def execute_safe(self, query: str, params: Tuple = (), fetch: bool = False):
        """
        Exécute une requête SQL avec gestion centralisée des erreurs.
        
        :param query: Requête SQL à exécuter.
        :param params: Paramètres de la requête.
        :param fetch: Indique si les résultats doivent être récupérés.
        :return: Résultats de la requête (si fetch est True), sinon None.
        """
        try:
            self.cursor.execute(query, params)
            if fetch:
                return self.cursor.fetchall()  # Retourner les résultats si demandé
            else:
                self.connection.commit()  # Valider les modifications
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            self.connection.rollback()  # Annuler la transaction en cas d'erreur
            raise RuntimeError(f"Erreur SQL : {e} | Query : {query} | Params : {params}")


    def fetch_by_condition(self, table_name: str, condition: str, params: Tuple = ()) -> List[Tuple]:
        """Récupère les données d'une table avec une condition."""
        query = f"SELECT * FROM {table_name} WHERE {condition}"
        try:
            self.cursor.execute(query, params)
            return self.execute_safe(query, params, fetch=True)
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
   

    def update_data(self, table_name: str, set_clause: str, condition: str, params: Tuple) -> None:
        """Met à jour des données dans une table."""
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        try:
            self.cursor.execute(query, params)
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
        finally:
            self.connection.commit()

    def delete_data(self, table_name: str, condition: str, params: Tuple) -> None:
        """Supprime des données d'une table selon une condition."""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        try:
            self.cursor.execute(query, params)
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
        finally:
            self.connection.commit()

    def close_connection(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def create_index(self, table_name: str, column_name: str) -> None:
        """Crée un index sur une colonne spécifique pour améliorer les performances de recherche."""
        query = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name} ({column_name})"
        try:
            self.cursor.execute(query)
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
        finally:
            self.connection.commit()

    def select(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Exécute une requête SELECT personnalisée et retourne les résultats."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
    
    def query(self, query, params=None):
        """
        Exécute une requête SQL, en utilisant les paramètres fournis, 
        et retourne les résultats si nécessaire.
        """
        try:
            self.cursor.execute(query, params)
        except psycopg2.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return
        finally:
            # Si la requête est un SELECT, récupérer les résultats
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            else: # Si ce n'est pas un SELECT, ne rien retourner (utile pour INSERT/UPDATE)
                self.connection.commit()
                return None  
        


    

######################### FONCTIONS #########################

# Mettre DBManager en cache
@st.cache_resource
def get_db_manager():
    return DBManager(db_config, os.path.join("server","db","schema.json"))


def save_message(db_manager, id_conversation: int, role: str, content: str) -> None:
    """
    Sauvegarde un message dans la base de données, en associant l'utilisateur à la conversation.
    
    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation associée.
    :param role: Rôle de l'intervenant (ex. 'user' ou 'assistant').
    :param content: Contenu du message.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [{
        "id_conversation": id_conversation,
        "role": role,
        "content": content,
        "timestamp": timestamp,
    }]
    try:
        db_manager.insert_data_from_dict("messages", data, id_column="id_message")
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return    

def create_conversation(db_manager, title: str, id_utilisateur: int) -> int:
    """
    Crée une nouvelle conversation dans la base de données, en associant l'utilisateur à la conversation.
    
    :param db_manager: Instance de DBManager.
    :param title: Titre de la conversation.
    :param id_utilisateur: ID de l'utilisateur associé.
    :return: ID de la conversation nouvellement créée.
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [{
        "created_at": created_at,
        "title": title,
        "id_utilisateur": id_utilisateur,
    }]
    try:
        result = db_manager.insert_data_from_dict("conversations", data, id_column="id_conversation")
        logger.warning(type(result))
        return result[0]
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return

def load_messages(db_manager, id_conversation: int) -> List[Dict]:
    """
    Charge les messages associés à une conversation.
    
    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation.
    :return: Liste des messages sous forme de dictionnaires.
    """
    query = """
        SELECT role, content 
        FROM messages 
        WHERE id_conversation = %s 
        ORDER BY timestamp ASC
    """
    try:
        result = db_manager.query(query, (id_conversation,))
        return [{"role": row[0], "content": row[1]} for row in result]
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return

def load_conversations(db_manager, id_utilisateur: int) -> List[Dict]:
    """
    Charge toutes les conversations enregistrées pour un utilisateur donné.
    
    :param db_manager: Instance de DBManager.
    :param id_utilisateur: ID de l'utilisateur.
    :return: Liste des conversations.
    """
    query = """
        SELECT * FROM conversations 
        WHERE id_utilisateur = %s
        ORDER BY created_at DESC
    """
    try:
        result = db_manager.query(query, (id_utilisateur,))
        print("Résultat de la requête SQL :", result)

        return [
            {"id_conversation": row["id_conversation"], "created_at": row["created_at"], "title": row["title"]} for row in result
        ]
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return

def update_conversation(db_manager, id_conversation: int, id_utilisateur: int) -> None:
    """
    Met à jour le champ `created_at` d'une conversation donnée pour un utilisateur.
    
    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation à mettre à jour.
    :param id_utilisateur: ID de l'utilisateur.
    """
    new_timer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = """
        UPDATE conversations 
        SET created_at = %s 
        WHERE id_conversation = %s AND id_utilisateur = %s
    """
    try:
        db_manager.query(query, (new_timer, id_conversation, id_utilisateur))
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return

def update_conversation_title(db_manager, id_conversation: int, new_title: str) -> None:
    """
    Met à jour le titre d'une conversation si celui-ci est encore "Nouvelle conversation".

    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation à mettre à jour.
    :param new_title: Nouveau titre de la conversation.
    """
    query = """
        UPDATE conversations 
        SET title = %s
        WHERE id_conversation = %s AND title = 'Nouvelle conversation'
    """
    try:
        db_manager.query(query, (new_title, id_conversation))
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return

def get_conversation_title(db_manager, id_conversation: int) -> str:
    """
    Récupère le titre d'une conversation spécifique en utilisant `fetch_by_condition`.

    :param db_manager: Instance de DBManager.
    :param id_conversation: ID de la conversation à interroger.
    :return: Le titre de la conversation ou "Nouvelle conversation".
    """
    table_name = "conversations"
    condition = "id_conversation = %s"
    try:
        results = db_manager.fetch_by_condition(table_name, condition, (id_conversation,))
        if results:
            # Suppose que `title` est la troisième colonne
            return results[0][2]
        return "Nouvelle conversation"
    except psycopg2.Error as err:
        logger.error(f"Error while connecting to database: {err}")
        return