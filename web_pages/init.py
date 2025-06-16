"""
Página de inicio de la aplicación del dashboar de la UNED
"""

import streamlit as st

st.header("Bienvenido al dashboard para la gestión de auditorías de accesibilidad web de la UNED", anchor=False)


st.html("<p>Este dashboard permitirá hacer una gestión integral de las auditorias de accesibilidad web de la UNED. " \
"En la barra lateral podrá encontrar las diferentes páginas que componen esta aplicación y que son las siguientes.</p>")

st.html("<h3>Gestión de ficheros</h3>")

st.html("<p>Permitirá cargar nuevos ficheros y almacenarlos internamente.</p>")

st.html("<h3>Visualización de datos</h3>")

st.html("<p>Permitirá visualizar los datos cargados así como realizar filtros sobre ellos" \
" y la visualización de parámetros estadísticos y geográficos asociados a los mismos.</p>")

st.html("<h3>Calidad de datos</h3>")

st.html("<p>Permitirá realizar algunas acciones sobre los datos en caso de problemas de calidad  como puedan ser valores que faltan, " \
"ya sea eliminándolos o rellenándolos con alguna medida de tendencia central por ejemplo.</p>")

st.html("<h3>Chatbot de consulta</h3>")

st.html("<p>Permitirá realizar todo tipo de consultas a un chatbot.</p>")

