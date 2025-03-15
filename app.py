import streamlit as st

st.set_page_config(
    page_title="Aplicación de análisis de accesibilidad wcag de la UNED",
    page_icon="👋",
    layout="wide"
)

pagina_inicio = st.Page("./web_pages/init.py", title= "Inicio")
pagina_gestion = st.Page("./web_pages/gestion.py", title= "Gestión de ficheros")
pagina_visualizacion = st.Page("./web_pages/visualizacion.py", title= "Visualización de datos")

pg = st.navigation([pagina_inicio, pagina_gestion, pagina_visualizacion])
pg.run()
