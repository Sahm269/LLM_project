import psycopg2
from psycopg2 import extras
import json
import pandas as pd
from typing import List, Dict, Tuple
import os


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
        

    def _load_schema(self):
        """Charge le schéma de base de données depuis un fichier JSON."""
        if not os.path.exists(self.schema_file):
            raise FileNotFoundError(f"Fichier non trouvé : {self.schema_file}")
        
        with open(self.schema_file, "r", encoding="utf-8") as file:
            self.schema = json.load(file)

    def _connect_to_database(self):
        """Établit une connexion avec la base PostgreSQL."""
        try:
            self.connection = psycopg2.connect(**self.db_config, cursor_factory=extras.DictCursor)
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise ConnectionError(f"Erreur de connexion : {e}")

    def _create_database(self):
        """Crée les tables définies dans le schéma JSON."""
        for table_name, table_info in self.schema['tables'].items():
            create_table_query = self._generate_create_table_query(table_name, table_info['columns'])
            self.cursor.execute(create_table_query)
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
        for row in data:
            self.execute_safe(query, tuple(row.values()), fetch=True)  # Exécute la requête et récupère l'ID retourné
            inserted_id = self.cursor.fetchone()[0]  # Récupère le premier (et unique) élément de la ligne retournée
            ids.append(inserted_id)
        
        return ids



    def insert_data_from_csv(self, table_name: str, csv_file: str) -> None:
        """Insère des données dans une table à partir d'un fichier CSV."""
        df = pd.read_csv(csv_file)
        columns = df.columns.tolist()
        placeholders = ", ".join(['%s' for _ in columns])
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        for row in df.itertuples(index=False, name=None):
            self.cursor.execute(query, row)
        self.connection.commit()

    def fetch_all(self, table_name: str) -> List[Tuple]:
        """Récupère toutes les données d'une table."""
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()
    
    
    def execute_safe(self, query: str, params: Tuple = (), fetch: bool = False):
        """
        Exécute une requête SQL avec gestion des erreurs et des transactions.

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
        except Exception as e:
            self.connection.rollback()  # Annuler la transaction en cas d'erreur
            raise RuntimeError(f"Erreur SQL : {e} | Query : {query} | Params : {params}")



    def fetch_by_condition(self, table_name: str, condition: str, params: Tuple = ()) -> List[Tuple]:
        """Récupère les données d'une table avec une condition."""
        query = f"SELECT * FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, params)
        return self.execute_safe(query, params, fetch=True)
   

    def update_data(self, table_name: str, set_clause: str, condition: str, params: Tuple) -> None:
        """Met à jour des données dans une table."""
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self.cursor.execute(query, params)
        self.connection.commit()

    def delete_data(self, table_name: str, condition: str, params: Tuple) -> None:
        """Supprime des données d'une table selon une condition."""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.cursor.execute(query, params)
        self.connection.commit()

    def close_connection(self) -> None:
        """Ferme la connexion à la base de données."""
        if self.connection:
            self.cursor.close()
            self.connection.close()

    def create_index(self, table_name: str, column_name: str) -> None:
        """Crée un index sur une colonne spécifique pour améliorer les performances de recherche."""
        query = f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name} ({column_name})"
        self.execute_safe(query)

    def select(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Exécute une requête SELECT personnalisée et retourne les résultats."""
        return self.execute_safe(query, params, fetch=True)

    def query(self, query: str, params=None):
        """
        Exécute une requête SQL, en utilisant les paramètres fournis, 
        et retourne les résultats si nécessaire.
        """
        return self.execute_safe(query, params, fetch=True)
