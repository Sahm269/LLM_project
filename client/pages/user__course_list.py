import streamlit as st
from server.db.db import get_ingredients


# Page des courses
def course_list():
    st.write("Voici votre liste des courses.")
    
    ingredients_list = get_ingredients()
    
    if ingredients_list:
        for ingredient in ingredients_list:
            st.write(f"🍎 {ingredient[0]}")
    else:
        st.write("Aucun ingrédient trouvé.")

    st.checkbox("Ajouter un nouvel article")


