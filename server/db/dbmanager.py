import streamlit as st
import psycopg2
import sqlite3
from psycopg2 import extras
from datetime import datetime
import logging
import json
import pandas as pd
from typing import List, Dict, Tuple
import os
import sys
import unicodedata
# Configuration du logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

sys.stdout.reconfigure(encoding="utf-8")

# Configuration de la base de données
db_config = {
    "database": st.secrets["DB_NAME"],
    # "user": st.secrets["DB_USER"],
    # "password": st.secrets["DB_PASSWORD"],
    # "host": st.secrets["DB_HOST"],
    # "port": st.secrets["DB_PORT"]
}

######################### CLASSES #########################


class DBManager:
    def __init__(self, db_config: Dict, schema_file: str) -> None:
        """
        Initialise la connexion à la base PostgreSQL et charge le schéma.

        Args:
            db_config (Dict) : dictionnaire avec les informations de connexion (host, database, user, password).
            schema_file (str) : chemin vers le fichier JSON contenant le schéma de la base.
        """

        self.db_config = db_config
        self.schema_file = schema_file
        self.connection = None
        self.cursor = None
        self._load_schema()
        self._connect_to_database()
        self._create_database()
        # self.cursor.execute("SET NAMES 'UTF8'")

    def _load_schema(self) -> None:
        """
        Charge le schéma de base de données depuis un fichier JSON.
        """
        if not os.path.exists(self.schema_file):
            raise FileNotFoundError(f"Fichier non trouvé : {self.schema_file}")

        with open(self.schema_file, "r", encoding="utf-8") as file:
            self.schema = json.load(file)

    # def _connect_to_database(self):
    #     """Établit une connexion avec la base PostgreSQL."""
    #     try:
    #         self.connection = psycopg2.connect(**self.db_config, cursor_factory=extras.DictCursor)
    #         self.cursor = self.connection.cursor()
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return

    def _connect_to_database(self) -> None:
        """
        Établit une connexion avec la base SQLite.
        """
        try:
            # Connexion à la base de données SQLite
            self.connection = sqlite3.connect(
                self.db_config["database"], check_same_thread=False
            )
            self.connection.row_factory = (
                sqlite3.Row
            )  # Pour des résultats sous forme de dictionnaire
            self.cursor = self.connection.cursor()
        except sqlite3.Error as err:
            logger.error(f"Erreur de connexion : {err}")
            return

    # def _create_database(self):
    #     """Crée les tables définies dans le schéma JSON."""
    #     for table_name, table_info in self.schema['tables'].items():
    #         create_table_query = self._generate_create_table_query(table_name, table_info['columns'])
    #         try:
    #             self.cursor.execute(create_table_query)
    #         except psycopg2.Error as err:
    #             logger.error(f"Erreur de connexion : {err}")
    #             return
    #         finally:
    #             self.connection.commit()

    import sqlite3

    def _create_database(self) -> None:
        """
        Crée les tables définies dans le schéma JSON.
        """
        for table_name, table_info in self.schema["tables"].items():
            create_table_query = self._generate_create_table_query(
                table_name, table_info["columns"]
            )
            try:
                self.cursor.execute(create_table_query)
            except sqlite3.Error as err:
                logger.error(
                    f"Erreur lors de la création de la table {table_name}: {err}"
                )
                return
            finally:
                self.connection.commit()

    # def _generate_create_table_query(self, table_name: str, columns: List[Dict]) -> str:
    #     """Génère une requête SQL pour créer une table en fonction du schéma."""
    #     column_definitions = []
    #     for column in columns:
    #         column_definition = f"{column['name']} {column['type']}"
    #         if 'constraints' in column and column['constraints']:
    #             column_definition += " " + " ".join(column['constraints'])
    #         column_definitions.append(column_definition)
    #     columns_str = ", ".join(column_definitions)
    #     return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"

    def _generate_create_table_query(self, table_name: str, columns: List[Dict]) -> str:
        """
        Génère une requête SQL pour créer une table en fonction du schéma.

        Args:
            table_name (str): nom de la table.
            columns (List[Dict]): colonnes de la table à créer.
        
        Returns:
            str : la requête SQL CREATE TABLE paramétrée.

        """
        column_definitions = []
        for column in columns:
            column_definition = f"{column['name']} {column['type']}"

            # Conversion quand le type n'est pas compatible avec SQLite (ex. : SERIAL -> INTEGER PRIMARY KEY AUTOINCREMENT)
            if column["type"] == "SERIAL":
                column_definition = (
                    f"{column['name']} INTEGER PRIMARY KEY AUTOINCREMENT"
                )

            if "constraints" in column and column["constraints"]:
                column_definition += " " + " ".join(column["constraints"])

            column_definitions.append(column_definition)

        columns_str = ", ".join(column_definitions)
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"

    # def insert_data_from_dict(self, table_name: str, data: List[Dict], id_column: str) -> List[int]:
    #     """Insère des données dans une table à partir d'une liste de dictionnaires et retourne les IDs insérés.

    #     table_name : str : nom de la table
    #     data : List[Dict] : données à insérer
    #     id_column : str : nom de la colonne d'ID à retourner
    #     """
    #     columns = ", ".join(data[0].keys())
    #     placeholders = ", ".join(['%s' for _ in data[0].keys()])

    #     # Requête pour insérer les données et retourner l'ID dynamique
    #     query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING {id_column}"

    #     ids = []
    #     try:
    #         for row in data:
    #             self.cursor.execute(query, tuple(row.values()))
    #             inserted_id = self.cursor.fetchone()[0]
    #             ids.append(inserted_id)
    #         return ids
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return
    #     finally:
    #         self.connection.commit()

    def insert_data_from_dict(self, table_name: str, data: List[Dict]) -> List[int]:
        """
        Insère des données dans une table à partir d'une liste de dictionnaires et retourne les IDs insérés.
        
        Args:
            table_name (str): nom de la table.
            data (List[Dict]): données à insérer.
        
        Returns:
            List[int]: liste des ID des données insérées.
        """
        columns = ", ".join(data[0].keys())
        placeholders = ", ".join(
            ["?" for _ in data[0].keys()]
        )  # SQLite utilise '?' pour les placeholders

        # Requête pour insérer les données
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        ids = []
        try:
            for row in data:
                self.cursor.execute(query, tuple(row.values()))
                inserted_id = (
                    self.cursor.lastrowid
                )  # Récupère l'ID du dernier enregistrement inséré
                ids.append(inserted_id)
            return ids
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de l'insertion des données dans {table_name}: {err}"
            )
            return
        finally:
            self.connection.commit()

    # def insert_data_from_csv(self, table_name: str, csv_file: str) -> None:
    #     """Insère des données dans une table à partir d'un fichier CSV."""
    #     df = pd.read_csv(csv_file)
    #     columns = df.columns.tolist()
    #     placeholders = ", ".join(['%s' for _ in columns])
    #     query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

    #     try:
    #         for row in df.itertuples(index=False, name=None):
    #             self.cursor.execute(query, row)
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return
    #     finally:
    #         self.connection.commit()

    def insert_data_from_csv(self, table_name: str, csv_file: str) -> None:
        """
        Insère des données dans une table à partir d'un fichier CSV.
        
        Args:
            table_name (str): nom de la table dans laquelle insérer des données.
            csv_file (str): lien du fichier csv contenant les données.
        """
        df = pd.read_csv(csv_file)
        columns = df.columns.tolist()
        placeholders = ", ".join(
            ["?" for _ in columns]
        )  # Utilisation de '?' pour SQLite
        query = (
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        )

        try:
            for row in df.itertuples(index=False, name=None):
                self.cursor.execute(
                    query, row
                )  # Exécution de la requête avec les valeurs du CSV
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de l'insertion des données depuis {csv_file} : {err}"
            )
        finally:
            self.connection.commit()

    # def fetch_all(self, table_name: str) -> List[Tuple]:
    #     """
    #     Récupère toutes les données d'une table.

    #     Args:
    #         table_name (str): nom de la table de laquelle récupérer des données.

    #     Returns:
    #         List[Tuple]: liste des enregistrements récupérés à partir de la table.
    #     """
    #     try:
    #         self.cursor.execute(f"SELECT * FROM {table_name}")
    #         return self.cursor.fetchall()
    #     except sqlite3.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return

    def fetch_all(self, table_name: str) -> List[Tuple]:
        """
        Récupère toutes les données d'une table.
        
        Args:
            table_name (str): nom de la table de laquelle récupérer des données.

        Returns:
            List[Tuple]: liste des enregistrements récupérés à partir de la table.
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de la récupération des données de la table {table_name} : {err}"
            )
            return []  # Retourne une liste vide en cas d'erreur

    # def execute_safe(self, query: str, params: Tuple = (), fetch: bool = False):
    #     """
    #     Exécute une requête SQL avec gestion centralisée des erreurs.

    #     :param query: Requête SQL à exécuter.
    #     :param params: Paramètres de la requête.
    #     :param fetch: Indique si les résultats doivent être récupérés.
    #     :return: Résultats de la requête (si fetch est True), sinon None.
    #     """
    #     try:
    #         self.cursor.execute(query, params)
    #         if fetch:
    #             return self.cursor.fetchall()  # Retourner les résultats si demandé
    #         else:
    #             self.connection.commit()  # Valider les modifications
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         self.connection.rollback()  # Annuler la transaction en cas d'erreur
    #         raise RuntimeError(f"Erreur SQL : {err} | Query : {query} | Params : {params}")

    def execute_safe(
        self, query: str, params: Tuple = (), fetch: bool = False
    ) -> List[Tuple]:
        """
        Exécute une requête SQL avec gestion centralisée des erreurs.
        
        Args:
            query (str): requête SQL à exécuter.
            params (Tuple): paramètres de la requête.
            fetch (bool): indique si les résultats doivent être récupérés.
        
        Returns:
            List[Tuple]: résultats de la requête (si fetch est True), sinon None.
        """
        try:
            self.cursor.execute(query, params)
            if fetch:
                return self.cursor.fetchall()  # Retourner les résultats si demandé
            else:
                self.connection.commit()  # Valider les modifications
        except sqlite3.Error as err:
            logger.error(f"Erreur lors de l'exécution de la requête : {err}")
            self.connection.rollback()  # Annuler la transaction en cas d'erreur
            raise RuntimeError(
                f"Erreur SQL : {err} | Query : {query} | Params : {params}"
            )

    # def fetch_by_condition(self, table_name: str, condition: str, params: Tuple = ()) -> List[Tuple]:
    #     """Récupère les données d'une table avec une condition."""
    #     query = f"SELECT * FROM {table_name} WHERE {condition}"
    #     try:
    #         self.cursor.execute(query, params)
    #         return self.execute_safe(query, params, fetch=True)
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return

    def fetch_by_condition(
        self, table_name: str, condition: str, params: Tuple = ()
    ) -> List[Tuple]:
        """
        Récupère les données d'une table avec une condition.
        
        Args:
            table_name (str): nom de la table de laquelle récupérer des données.
            condition (str): condition qui sera inclue dans la clause WHERE pour filtrage.
            params (Tuple): paramètres de la requête.

        Returns:
            List[Tuple]: résultats de la requête (si fetch est True), sinon None (via la fonction execute_safe).
        """
        query = f"SELECT * FROM {table_name} WHERE {condition}"
        try:
            # Utilise execute_safe pour exécuter la requête et récupérer les résultats
            return self.execute_safe(query, params, fetch=True)
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de la récupération des données de {table_name} avec condition '{condition}': {err}"
            )
            return []

    # def update_data(self, table_name: str, set_clause: str, condition: str, params: Tuple) -> None:
    #     """Met à jour des données dans une table."""
    #     query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
    #     try:
    #         self.cursor.execute(query, params)
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return
    #     finally:
    #         self.connection.commit()

    def update_data(
        self, table_name: str, set_clause: str, condition: str, params: Tuple
    ) -> None:
        """
        Met à jour des données dans une table.
        
        Args:
            table_name (str): nom de la table dont les données vont être mises à jour.
            set_clause (str): information qui sera inclue dans la clause SET pour la mise à jour.
            condition (str): condition qui sera inclue dans la clause WHERE pour filtrage.
            params (Tuple): paramètres de la requête.
        """
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        try:
            self.cursor.execute(query, params)
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de la mise à jour des données dans {table_name} : {err}"
            )
        finally:
            self.connection.commit()  # Valider les modifications

    # def delete_data(self, table_name: str, condition: str, params: Tuple) -> None:
    #     """Supprime des données d'une table selon une condition."""
    #     query = f"DELETE FROM {table_name} WHERE {condition}"
    #     try:
    #         self.cursor.execute(query, params)
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return
    #     finally:
    #         self.connection.commit()

    def delete_data(self, table_name: str, condition: str, params: Tuple) -> None:
        """
        Supprime des données d'une table selon une condition.
        
        Args:
            table_name (str): nom de la table dont les données vont être suprimées.
            condition (str): condition qui sera inclue dans la clause WHERE pour filtrage.
            params (Tuple): paramètres de la requête.
        """
        query = f"DELETE FROM {table_name} WHERE {condition}"
        try:
            self.cursor.execute(query, params)
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de la suppression des données dans {table_name} : {err}"
            )
        finally:
            self.connection.commit()  # Valider les modifications

    # def close_connection(self) -> None:
    #     """Ferme la connexion à la base de données."""
    #     if self.connection:
    #         self.cursor.close()
    #         self.connection.close()

    def close_connection(self) -> None:
        """
        Ferme la connexion à la base de données.
        """
        if self.connection:
            try:
                self.cursor.close()  # Fermer le curseur
                self.connection.close()  # Fermer la connexion
            except sqlite3.Error as err:
                logger.error(f"Erreur lors de la fermeture de la connexion : {err}")

    # def create_index(self, table_name: str, column_name: str) -> None:
    #     """Crée un index sur une colonne spécifique pour améliorer les performances de recherche."""
    #     query = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name} ({column_name})"
    #     try:
    #         self.cursor.execute(query)
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return
    #     finally:
    #         self.connection.commit()

    def create_index(self, table_name: str, column_name: str) -> None:
        """
        Crée un index sur une colonne spécifique pour améliorer les performances de recherche.
        """
        query = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name} ({column_name})"
        try:
            self.cursor.execute(query)
        except sqlite3.Error as err:
            logger.error(
                f"Erreur lors de la création de l'index sur {table_name} ({column_name}) : {err}"
            )
        finally:
            self.connection.commit()  # Valider les modifications

    # def select(self, query: str, params: Tuple = ()) -> List[Tuple]:
    #     """Exécute une requête SELECT personnalisée et retourne les résultats."""
    #     try:
    #         self.cursor.execute(query, params)
    #         return self.cursor.fetchall()
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return

    def select(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Exécute une requête SELECT personnalisée et retourne les résultats.
        
        Args:
            query (str): requête SELECT.
            params (Tuple): paramètres de la requête.

        Returns:
            List[Tuple]: liste des enregistrements récupérés.
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as err:
            logger.error(f"Erreur lors de l'exécution de la requête SELECT : {err}")
            return []

    # def query(self, query, params=None):
    #     """
    #     Exécute une requête SQL, en utilisant les paramètres fournis,
    #     et retourne les résultats si nécessaire.
    #     """
    #     try:
    #         self.cursor.execute(query, params)
    #     except psycopg2.Error as err:
    #         logger.error(f"Erreur de connexion : {err}")
    #         return
    #     finally:
    #         # Si la requête est un SELECT, récupérer les résultats
    #         if query.strip().upper().startswith("SELECT"):
    #             return self.cursor.fetchall()
    #         else: # Si ce n'est pas un SELECT, ne rien retourner (utile pour INSERT/UPDATE)
    #             self.connection.commit()
    #             return None

    def query(self, query: str, params: Tuple = None) -> List[Tuple]:
        """
        Exécute une requête SQL, en utilisant les paramètres fournis, et retourne les résultats si nécessaire.

        Args:
            query (str): reqête SQL.
            params (Tuple): paramètres de la requête.

        Returns:
            List[Tuple]: list des enregistrements récupérés s'il s'agit d'une requête SELECT, None sinon.
        """
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
        except sqlite3.Error as err:
            logger.error(f"Erreur lors de l'exécution de la requête : {err}")
            return
        finally:
            # Si la requête est un SELECT, récupérer les résultats
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            else:  # Si ce n'est pas un SELECT, ne rien retourner (utile pour INSERT/UPDATE)
                self.connection.commit()
                return None


######################### FONCTIONS #########################

# Mettre DBManager en cache
@st.cache_resource
def get_db_manager():
    return DBManager(db_config, os.path.join("server", "db", "schema.json"))


# def save_message(db_manager, id_conversation: int, role: str, content: str,temps_traitement, total_cout, impact_eco) -> None:
#     """
#     Sauvegarde un message dans la base de données, en associant l'utilisateur à la conversation.

#     :param db_manager: Instance de DBManager.
#     :param id_conversation: ID de la conversation associée.
#     :param role: Rôle de l'intervenant (ex. 'user' ou 'assistant').
#     :param content: Contenu du message.
#     """
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     data = [{
#         "id_conversation": id_conversation,
#         "role": role,
#         "content": content,
#         "timestamp": timestamp,
#         "temps_traitement":temps_traitement,
#         "total_cout": total_cout,
#         "impact_eco": impact_eco
#     }]
#     try:
#         db_manager.insert_data_from_dict("messages", data, id_column="id_message")
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion: {err}")
#         return


def save_message(
    db_manager,
    id_conversation: int,
    role: str,
    content: str,
    temps_traitement: float,
    total_cout: float,
    impact_eco: float,
) -> None:
    """
    Sauvegarde un message dans la base de données, en associant l'utilisateur à la conversation.
    
    Args:
        db_manager: instance de DBManager.
        id_conversation (int): ID de la conversation associée.
        role (str): rôle de l'intervenant (ex. 'user' ou 'assistant').
        content (str): contenu du message.
        temps_traitement (float): temps de traitement.
        total_cout (float): coût total associé au message.
        impact_eco (float): impact économique du message.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [
        {
            "id_conversation": id_conversation,
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "temps_traitement": temps_traitement,
            "total_cout": total_cout,
            "impact_eco": impact_eco,
        }
    ]

    try:
        # Insertion des données dans la table "messages" en utilisant la méthode d'insertion adaptée
        db_manager.insert_data_from_dict("messages", data)
    except sqlite3.Error as err:  # Utilisation de sqlite3.Error pour gérer les exceptions SQLite
        logger.error(f"Erreur lors de la sauvegarde du message : {err}")
        return


# def create_conversation(db_manager, title: str, id_utilisateur: int) -> int:
#     """
#     Crée une nouvelle conversation dans la base de données, en associant l'utilisateur à la conversation.

#     :param db_manager: Instance de DBManager.
#     :param title: Titre de la conversation.
#     :param id_utilisateur: ID de l'utilisateur associé.
#     :return: ID de la conversation nouvellement créée.
#     """
#     created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     data = [{
#         "created_at": created_at,
#         "title": title,
#         "id_utilisateur": id_utilisateur,
#     }]
#     try:
#         result = db_manager.insert_data_from_dict("conversations", data, id_column="id_conversation")
#         return result[0]
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion : {err}")
#         return


def create_conversation(db_manager, title: str, id_utilisateur: int) -> int:
    """
    Crée une nouvelle conversation dans la base de données, en associant l'utilisateur à la conversation.
    
    Args:
        db_manager: instance de DBManager.
        title (str): titre de la conversation.
        id_utilisateur (int): ID de l'utilisateur associé.

    Returns:
        int: ID de la conversation nouvellement créée.
        
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [
        {"created_at": created_at, "title": title, "id_utilisateur": id_utilisateur,}
    ]

    try:
        result = db_manager.insert_data_from_dict("conversations", data)
        return result[0]  # Retourne l'ID de la conversation nouvellement créée
    except sqlite3.Error as err:  # Gestion des erreurs avec sqlite3
        logger.error(f"Erreur lors de la création de la conversation : {err}")
        return None


# def load_messages(db_manager, id_conversation: int) -> List[Dict]:
#     """
#     Charge les messages associés à une conversation.

#     :param db_manager: Instance de DBManager.
#     :param id_conversation: ID de la conversation.
#     :return: Liste des messages sous forme de dictionnaires.
#     """
#     query = """
#         SELECT *
#         FROM messages
#         WHERE id_conversation = %s
#         ORDER BY timestamp ASC
#     """
#     try:
#         result = db_manager.query(query, (id_conversation,))
#         return [{"role": row["role"], "content": row["content"], "timestamp":row["timestamp"], "temps_traitement":row["temps_traitement"]} for row in result]
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion : {err}")
#         return


def load_messages(db_manager, id_conversation: int) -> List[Dict]:
    """
    Charge les messages associés à une conversation.
    
    Args:
        db_manager: instance de DBManager.
        id_conversation (int): ID de la conversation.
    Returns:
        List[Dict]: liste des messages sous forme de dictionnaires.
    """
    query = """
        SELECT role, content, timestamp, temps_traitement
        FROM messages 
        WHERE id_conversation = ? 
        ORDER BY timestamp ASC
    """
    try:
        result = db_manager.query(query, (id_conversation,))
        # Résultats sous forme de dictionnaires, si la fonction query retourne des tuples ou dictionnaires
        return [
            {
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["timestamp"],
                "temps_traitement": row["temps_traitement"],
            }
            for row in result
        ]
    except sqlite3.Error as err:  # Utilisation de sqlite3.Error pour capturer les erreurs SQLite
        logger.error(f"Erreur lors du chargement des messages : {err}")
        return []


# def load_conversations(db_manager, id_utilisateur: int) -> List[Dict]:
#     """
#     Charge toutes les conversations enregistrées pour un utilisateur donné.

#     :param db_manager: Instance de DBManager.
#     :param id_utilisateur: ID de l'utilisateur.
#     :return: Liste des conversations.
#     """
#     query = """
#         SELECT * FROM conversations
#         WHERE id_utilisateur = %s
#         ORDER BY created_at DESC
#     """
#     try:
#         result = db_manager.query(query, (id_utilisateur,))


#         return [
#             {"id_conversation": row["id_conversation"], "created_at": row["created_at"], "title": row["title"]} for row in result
#         ]
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion : {err}")
#         return


def load_conversations(db_manager, id_utilisateur: int) -> List[Dict]:
    """
    Charge toutes les conversations enregistrées pour un utilisateur donné.
    
    Args:
        db_manager: instance de DBManager.
        id_utilisateur (int): ID de l'utilisateur.
    Returns:
        List[Dict]: liste des conversations.
    """
    query = """
        SELECT id_conversation, created_at, title
        FROM conversations 
        WHERE id_utilisateur = ? 
        ORDER BY created_at DESC
    """
    try:
        result = db_manager.query(query, (id_utilisateur,))
        return [
            {
                "id_conversation": row["id_conversation"],
                "created_at": row["created_at"],
                "title": row["title"],
            }
            for row in result
        ]
    except sqlite3.Error as err:  # Gestion des erreurs avec sqlite3
        logger.error(f"Erreur lors du chargement des conversations : {err}")
        return []


# def update_conversation(db_manager, id_conversation: int, id_utilisateur: int) -> None:
#     """
#     Met à jour le champ `created_at` d'une conversation donnée pour un utilisateur.

#     :param db_manager: Instance de DBManager.
#     :param id_conversation: ID de la conversation à mettre à jour.
#     :param id_utilisateur: ID de l'utilisateur.
#     """
#     new_timer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     query = """
#         UPDATE conversations
#         SET created_at = %s
#         WHERE id_conversation = %s AND id_utilisateur = %s
#     """
#     try:
#         db_manager.query(query, (new_timer, id_conversation, id_utilisateur))
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion : {err}")
#         return


def update_conversation(db_manager, id_conversation: int, id_utilisateur: int) -> None:
    """
    Met à jour le champ `created_at` d'une conversation donnée pour un utilisateur.
    
    Args:
        db_manager: instance de DBManager.
        id_conversation (int): ID de la conversation à mettre à jour.
        id_utilisateur (int): ID de l'utilisateur.
    """
    new_timer = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = """
        UPDATE conversations 
        SET created_at = ? 
        WHERE id_conversation = ? AND id_utilisateur = ?
    """
    try:
        db_manager.query(query, (new_timer, id_conversation, id_utilisateur))
    except sqlite3.Error as err:  # Utilisation de sqlite3.Error pour capturer les erreurs SQLite
        logger.error(f"Erreur lors de la mise à jour de la conversation : {err}")
        return


# def update_conversation_title(db_manager, id_conversation: int, new_title: str) -> None:
#     """
#     Met à jour le titre d'une conversation si celui-ci est encore "Nouvelle conversation".

#     :param db_manager: Instance de DBManager.
#     :param id_conversation: ID de la conversation à mettre à jour.
#     :param new_title: Nouveau titre de la conversation.
#     """
#     query = """
#         UPDATE conversations
#         SET title = %s
#         WHERE id_conversation = %s AND title = 'Nouvelle conversation'
#     """
#     try:
#         db_manager.query(query, (new_title, id_conversation))
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion : {err}")
#         return


def update_conversation_title(db_manager, id_conversation: int, new_title: str) -> None:
    """
    Met à jour le titre d'une conversation si celui-ci est encore "Nouvelle conversation".

    Args:
        db_manager: instance de DBManager.
        id_conversation (int): ID de la conversation à mettre à jour.
        new_title (str): nouveau titre de la conversation.
    """
    query = """
        UPDATE conversations 
        SET title = ? 
        WHERE id_conversation = ? AND title = 'Nouvelle conversation'
    """
    try:
        db_manager.query(query, (new_title, id_conversation))
    except sqlite3.Error as err:  # Utilisation de sqlite3.Error pour gérer les erreurs SQLite
        logger.error(
            f"Erreur lors de la mise à jour du titre de la conversation : {err}"
        )
        return


# def get_conversation_title(db_manager, id_conversation: int) -> str:
#     """
#     Récupère le titre d'une conversation spécifique en utilisant `fetch_by_condition`.

#     :param db_manager: Instance de DBManager.
#     :param id_conversation: ID de la conversation à interroger.
#     :return: Le titre de la conversation ou "Nouvelle conversation".
#     """
#     table_name = "conversations"
#     condition = "id_conversation = %s"
#     try:
#         results = db_manager.fetch_by_condition(table_name, condition, (id_conversation,))
#         if results:
#             # Suppose que `title` est la troisième colonne
#             return results[0][2]
#         return "Nouvelle conversation"
#     except psycopg2.Error as err:
#         logger.error(f"Erreur de connexion : {err}")
#         return


def get_conversation_title(db_manager, id_conversation: int) -> str:
    """
    Récupère le titre d'une conversation spécifique en utilisant `fetch_by_condition`.

    Args:
        db_manager: instance de DBManager.
        id_conversation (int): ID de la conversation à interroger.
    
    Returns:
        str: le titre de la conversation ou "Nouvelle conversation".
    """
    table_name = "conversations"
    condition = "id_conversation = ?"
    try:
        results = db_manager.fetch_by_condition(
            table_name, condition, (id_conversation,)
        )
        if results:
            # Assume that `title` is the second column
            return results[0][
                1
            ]  # 1 corresponds to the index of the title column in the result
        return "Nouvelle conversation"
    except sqlite3.Error as err:  # Utilisation de sqlite3.Error pour gérer les erreurs SQLite
        logger.error(
            f"Erreur lors de la récupération du titre de la conversation : {err}"
        )
        return "Nouvelle conversation"


# def delete_conversation(db_manager, id_conversation: int) -> None:
#     """
#     Supprime une conversation et ses messages associés de la base de données.

#     :param db_manager: Instance de DBManager.
#     :param id_conversation: ID de la conversation à supprimer.
#     """
#     try:
#         # Supprimer les messages liés à la conversation
#         query_delete_messages = "DELETE FROM messages WHERE id_conversation = %s"
#         db_manager.query(query_delete_messages, (id_conversation,))

#         # Supprimer la conversation elle-même
#         query_delete_conversation = "DELETE FROM conversations WHERE id_conversation = %s"
#         db_manager.query(query_delete_conversation, (id_conversation,))

#         print(f"✅ Conversation {id_conversation} supprimée avec succès.")
#     except Exception as e:
#         print(f"❌ Erreur lors de la suppression de la conversation {id_conversation}: {e}")


def delete_conversation(db_manager, id_conversation: int) -> None:
    """
    Supprime une conversation et ses messages associés de la base de données.

    Args:
        db_manager: instance de DBManager.
        id_conversation (int): ID de la conversation à supprimer.
    """
    try:
        # Supprimer les messages liés à la conversation
        query_delete_messages = "DELETE FROM messages WHERE id_conversation = ?"
        db_manager.query(query_delete_messages, (id_conversation,))

        # Supprimer la conversation elle-même
        query_delete_conversation = (
            "DELETE FROM conversations WHERE id_conversation = ?"
        )
        db_manager.query(query_delete_conversation, (id_conversation,))

        logger.info(f"✅ Conversation {id_conversation} supprimée avec succès.")
        # print(f"✅ Conversation {id_conversation} supprimée avec succès.")
    except sqlite3.Error as e:  # Utilisation de sqlite3.Error pour capturer les erreurs SQLite
        logger.error(
            f"❌ Erreur lors de la suppression de la conversation {id_conversation}: {e}"
        )
        # print(f"❌ Erreur lors de la suppression de la conversation {id_conversation}: {e}")


# def load_chatbot_suggestions(db_manager, user_id):
#     """
#     Charge les suggestions du chatbot enregistrées pour un utilisateur donné.
#     """
#     query = "SELECT repas_suggestion FROM suggestions_repas WHERE id_utilisateur = %s"
#     try:
#         db_manager.cursor.execute(query, (user_id,))
#         suggestions = [row[0] for row in db_manager.cursor.fetchall()]
#         return suggestions
#     except psycopg2.Error as err:
#         logger.error(f"Erreur lors du chargement des suggestions : {err}")
#         return []


def load_chatbot_suggestions(db_manager, user_id: str) -> List[Tuple]:
    """
    Charge les suggestions du chatbot enregistrées pour un utilisateur donné.

    Args:
        db_manager: instance de DBManager.
        user_id (int): ID de l'utilisateur.

    Returns:
        List[Tuple]: list des suggestions du chatbot.
    """
    query = "SELECT repas_suggestion FROM suggestions_repas WHERE id_utilisateur = ?"
    try:
        db_manager.cursor.execute(query, (user_id,))
        suggestions = [row[0] for row in db_manager.cursor.fetchall()]
        return suggestions
    except sqlite3.Error as err:  # Utilisation de sqlite3.Error pour capturer les erreurs SQLite
        logger.error(f"Erreur lors du chargement des suggestions : {err}")
        return []


# def save_chatbot_suggestions(db_manager, user_id, suggestions):
#     """
#     Sauvegarde les suggestions du chatbot dans la base de données.
#     """
#     query = """
#     INSERT INTO suggestions_repas (id_utilisateur, repas_suggestion, motif_suggestion)
#     VALUES (%s, %s, %s)
#     """
#     try:
#         for suggestion in suggestions:
#             db_manager.cursor.execute(query, (user_id, suggestion, "Chatbot"))
#         db_manager.connection.commit()
#     except psycopg2.Error as err:
#         logger.error(f"Erreur lors de l'enregistrement des suggestions : {err}")


def save_chatbot_suggestions(db_manager, user_id, suggestions: List[Tuple]):
    """
    Sauvegarde les suggestions du chatbot dans la base de données.

    Args:
        db_manager: instance de DBManager.
        user_id (int): ID de l'utilisateur.
        suggestions (List[Tuple]): list des suggestions du chatbot.

    """
    query = """
    INSERT INTO suggestions_repas (id_utilisateur, repas_suggestion, motif_suggestion) 
    VALUES (?, ?, ?)
    """
    try:
        for suggestion in suggestions:
            db_manager.cursor.execute(query, (user_id, suggestion, "Chatbot"))
        db_manager.connection.commit()
    except sqlite3.Error as err:  # Remplacer psycopg2.Error par sqlite3.Error pour SQLite
        logger.error(f"Erreur lors de l'enregistrement des suggestions : {err}")

def save_recipes_and_ingredients(db_manager, user_id: int, recipes: List[Dict[str, str]]):
    """
    Sauvegarde les recettes et leurs ingrédients en base de données.

    Args:
        db_manager: Instance de DBManager.
        user_id (int): ID de l'utilisateur.
        recipes (List[Dict[str, str]]): Liste des recettes contenant "titre" et "ingredients".
    """
    query_recipe = """
    INSERT INTO suggestions_repas (id_utilisateur, repas_suggestion, motif_suggestion, date_heure)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """

    query_ingredients = """
    INSERT INTO liste_courses (id_utilisateur, ingredients, date_creation, status)
    VALUES (?, ?, CURRENT_TIMESTAMP, 'non acheté')
    """

    try:
        for recipe in recipes:
            # Insérer le titre de la recette
            db_manager.cursor.execute(query_recipe, (user_id, recipe["titre"], "Chatbot"))
            
            # Insérer les ingrédients associés
            db_manager.cursor.execute(query_ingredients, (user_id, recipe["ingredients"]))
        
        db_manager.connection.commit()
    except sqlite3.Error as err:
        logger.error(f"❌ Erreur lors de l'enregistrement des recettes : {err}")


def normalize_text(text):
    """Normalise un texte en supprimant les accents et en le mettant en minuscules"""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return text

def save_recipes_with_ingredients(db_manager, user_id, title, ingredients):
    """
    Sauvegarde une recette et ses ingrédients en base de données,
    en évitant les doublons liés aux différences de majuscules ou d'accents.
    """
    if not ingredients:
        print(f"⚠️ La recette '{title}' n'a pas d'ingrédients à enregistrer.")
        return

    # 🔹 Normaliser le titre pour éviter les doublons
    normalized_title = normalize_text(title)

    # 🔹 Vérifier si la recette existe déjà (en ignorant les majuscules et accents)
    query_check = "SELECT id_suggestion FROM suggestions_repas WHERE LOWER(repas_suggestion) = LOWER(?) AND id_utilisateur = ?"
    result = db_manager.execute_safe(query_check, (normalized_title, user_id), fetch=True)

    if result:
        recipe_id = result[0][0]
        # 🔹 Mise à jour des ingrédients si la recette existe déjà
        query_update = "UPDATE suggestions_repas SET ingredients = ? WHERE id_suggestion = ?"
        db_manager.execute_safe(query_update, (ingredients, recipe_id))
        print(f"🔄 Mise à jour des ingrédients pour '{title}'.")
    else:
        # 🔹 Insertion d'une nouvelle recette avec son titre et ingrédients
        query_insert = "INSERT INTO suggestions_repas (id_utilisateur, repas_suggestion, ingredients) VALUES (?, ?, ?)"
        db_manager.execute_safe(query_insert, (user_id, title, ingredients))
        print(f"✅ Recette '{title}' enregistrée avec ingrédients.")



def get_recipes_and_ingredients(db_manager, user_id: int) -> List[Dict[str, str]]:
    """
    Récupère les recettes et leurs ingrédients stockés en base.

    Args:
        db_manager: Instance de DBManager.
        user_id (int): ID de l'utilisateur.

    Returns:
        List[Dict[str, str]]: Liste des recettes avec leurs ingrédients.
    """
    query = """
    SELECT repas_suggestion, ingredients 
    FROM suggestions_repas 
    WHERE id_utilisateur = ?
    """
    try:
        db_manager.cursor.execute(query, (user_id,))
        recipes = [{"titre": row[0], "ingredients": row[1]} for row in db_manager.cursor.fetchall()]
        return recipes
    except sqlite3.Error as err:
        print(f"❌ Erreur lors de la récupération des recettes : {err}")
        return []

def add_ingredients_column_if_not_exists(db_manager):
    """
    Vérifie et ajoute la colonne 'ingredients' à la table 'suggestions_repas' si elle n'existe pas.
    """
    try:
        db_manager.cursor.execute("PRAGMA table_info(suggestions_repas);")
        columns = [row[1] for row in db_manager.cursor.fetchall()]
        
        if "ingredients" not in columns:
            db_manager.cursor.execute("ALTER TABLE suggestions_repas ADD COLUMN ingredients TEXT;")
            db_manager.connection.commit()
            print("✅ Colonne 'ingredients' ajoutée avec succès.")
        else:
            print("✅ La colonne 'ingredients' existe déjà.")
    except sqlite3.Error as err:
        print(f"❌ Erreur lors de la mise à jour de la table : {err}")

def check_recipes_with_ingredients(db_manager, user_id):
    """
    Vérifie si les recettes enregistrées ont bien des ingrédients.
    """
    query = "SELECT repas_suggestion, ingredients FROM suggestions_repas WHERE id_utilisateur = ?"
    
    try:
        db_manager.cursor.execute(query, (user_id,))
        results = db_manager.cursor.fetchall()
        
        if results:
            print("✅ Recettes et ingrédients trouvés en base :")
            for row in results:
                print(f"📌 Recette: {row[0]} - Ingrédients: {row[1]}")
        else:
            print("⚠️ Aucune recette avec ingrédients trouvée en base.")

    except sqlite3.Error as err:
        print(f"❌ Erreur lors de la récupération des recettes : {err}")


