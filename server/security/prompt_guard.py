import os
from pickle import load, dump
import streamlit as st
import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer
from langdetect import detect

# Initialize the model once to avoid repeated loading
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def get_embedding(documents: list[str]) -> NDArray[np.float32]:
    """
    Generates embeddings for a list of documents using a pre-trained SentenceTransformer model.

    Args:
        documents (list[str]): A list of strings (documents) for which embeddings are to be generated.

    Returns:
        NDArray: A NumPy array containing the embeddings for each document.
    """
    if isinstance(documents, str):
        documents = [documents]
    return model.encode(documents)



class Guardrail:
    """
    A class to handle guardrail analysis based on query embeddings.

    Attributes:
        guardrail (Any): The guardrail model used for predictions.
    """

    def __init__(self):
        """
        Initializes the Guardrail class with a guardrail model instance.
        """
        file_path = os.path.join("server","security","storage","guardrail_multi.pkl")
        with open(file_path, "rb") as f:
            self.guardrail = load(f)

    def analyze_language(self, query:str) -> bool:
        """
        Analyzes the given query to determine what language it is written in and whether it is english, french, german or spanish.

        Args:
            query (str): The input query to be analyzed.

        Returns:
            bool: Returns `False` if the query is not a supported language, `True` otherwise.
        """
        det = detect(query)
        return det in ["en","fr","de","es"]
    
    def analyze_query(self, query: str) -> bool:
        """
        Analyzes the given query to determine if it passes the guardrail check.

        Args:
            query (str): The input query to be analyzed.

        Returns:
            bool: Returns `False` if the query is flagged, `True` otherwise.
        """
        embed_query = get_embedding(documents=[query])
        pred = self.guardrail.predict(embed_query.reshape(1, -1))
        return pred != 1  # Return True if pred is not 1, otherwise False
    

    def incremental_learning(self, X_new, y_new):
        """
        Allows to pursue the guardrail learning with new examples.

        Args:
            X_new (str) : string's prompt on which the guardrail is going to be partly fit for incremental training
            y_new (int) : class label of the prompt
        """
        # Extraction des caractéristiques
        embedding = model.encode(X_new)
        
        # Mise à jour incrémentale du modèle
        self.guardrail.partial_fit(embedding, y_new, classes=[0, 1])

        with open(os.path.join("server","security","storage","guardrail_multi.pkl"), "wb") as f:
            dump(self.guardrail, f)
