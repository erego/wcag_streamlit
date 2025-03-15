import streamlit as st

st.set_page_config(
    page_title="Aplicación de análisis de accesibilidad wcag de la UNED",
    page_icon="👋",
    layout="wide"
)

col1, col2, col3 = st.columns(3)
with col3:
    st.image("./static/logouned.png")

st.write("# Bienvenido al dashboard para la gestión de auditorías de accesibilidad web de la UNED")


st.markdown(
    """
    Este dashboard permitirá hacer una gestión integral de las auditorias de accesibilidad web de la UNED.
    En la barra lateral podrá encontrar las diferentes páginas que componen esta aplicación y que son las siguientes.
    
    ### Gestión de ficheros
    Permitirá cargar nuevos ficheros y almacenarlos internamente.

    ### Visualización
    Permitirá visualizar los datos cargados así como realizar filtros sobre ellos y la visualización de parámetros estadísticos y geográficos asociados a los mismos.

    ### Saneamiento de datos
    Permitirá realizar algunas acciones sobre los datos en caso de problemas de calidad como puedan ser valores que faltan, ya sea eliminándolos o rellenándolos con alguna medida de tendencia central por ejemplo.
    
"""
)



