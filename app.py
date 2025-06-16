"""Página de entrada de la aplicación multipágina de accesibilidad de la uned
"""

import streamlit as st

st.set_page_config(
    page_title="Aplicación de análisis de accesibilidad wcag de la UNED",
    page_icon="👋",
    layout="wide"
)

col1, col2 = st.columns([0.7, 0.3])

with col1:
    st.title("Dashboard de accesibilidad web de la UNED", anchor=False)

with col2:

    # st.image("./static/logo_informatica.gif", width=220)

    st.html("<img src='https://www.uned.es/universidad/.imaging/mte/site-facultades-theme/220/dam/recursos-corporativos/logotipos/facultades-escuelas/logo_informatica.gif/jcr:content/logo_informatica.gif' alt='Logo de la Escuela Técnica Superior de Ingeniería Informática de la UNED'>")
    st.html('<p style="color: black;">Logo de la Escuela Técnica Superior de Ingeniería Informática de la UNED.</p>')


pagina_inicio = st.Page("./web_pages/init.py", title= "Inicio")
pagina_gestion = st.Page("./web_pages/gestion.py", title= "Gestión de ficheros")
pagina_visualizacion = st.Page("./web_pages/visualizacion.py", title= "Visualización de datos")
pagina_calidad = st.Page("./web_pages/calidad.py", title= "Calidad de datos")
pagina_chatbot = st.Page("./web_pages/chatbot.py", title= "Chatbot de consulta")

pg = st.navigation([pagina_inicio, pagina_gestion, pagina_visualizacion, 
                    pagina_calidad, pagina_chatbot])
pg.run()
