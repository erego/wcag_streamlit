import streamlit as st
import sqlite3

st.set_page_config(
    page_title="Aplicación de análisis de accesibilidad wcag de la UNED",
    page_icon="👋",
    layout="wide"
)

col1, col2 = st.columns([0.7, 0.3])

with col1:
    st.write("# Dashboard de accesibilidad web de la UNED")

with col2:
    st.image("./static/logouned.png")


pagina_inicio = st.Page("./web_pages/init.py", title= "Inicio")
pagina_gestion = st.Page("./web_pages/gestion.py", title= "Gestión de ficheros")
pagina_visualizacion = st.Page("./web_pages/visualizacion.py", title= "Visualización de datos")
pagina_calidad = st.Page("./web_pages/calidad.py", title= "Calidad de datos")




pg = st.navigation([pagina_inicio, pagina_gestion, pagina_visualizacion, pagina_calidad])
pg.run()
