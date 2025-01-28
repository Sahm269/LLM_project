import streamlit as st

def course_list():
    st.subheader("Liste des courses")
    st.write("Voici votre liste des courses.")
    st.checkbox("Ajouter un nouvel article")
