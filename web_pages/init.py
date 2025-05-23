"""
Página de inicio de la aplicación del dashboar de la UNED
"""

import streamlit as st

st.write("## Bienvenido al dashboard para la gestión de auditorías de accesibilidad web de la UNED")


st.markdown(
    """
    Este dashboard permitirá hacer una gestión integral de las auditorias 
    de accesibilidad web de la UNED.
    En la barra lateral podrá encontrar las diferentes páginas que 
    componen esta aplicación y que son las siguientes.
    
    ### Gestión de ficheros
    Permitirá cargar nuevos ficheros y almacenarlos internamente.

    ### Visualización de datos
    Permitirá visualizar los datos cargados así como realizar filtros sobre ellos 
    y la visualización de parámetros estadísticos y geográficos asociados a los mismos.

    ### Calidad de datos
    Permitirá realizar algunas acciones sobre los datos en caso de problemas de calidad 
    como puedan ser valores que faltan, ya sea eliminándolos o rellenándolos 
    con alguna medida de tendencia central por ejemplo.
    
    ### Chatbot de consulta
    Permitirá realizar todo tipo de consultas a un chatbot.

"""
)
