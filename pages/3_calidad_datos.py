import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError

st.set_page_config(page_title="DataFrame Demo", page_icon="📊")

st.markdown("# Análisis y gestión de calidad de los datos")
st.sidebar.header("Calidad de los datos")
st.write(
    """En esta sección veremos algunos posibles problemas y se ofreceran algunas posibles soluciones"""
)




try:

    st.write(
        """En esta sección veremos algunos posibles problemas y se ofreceran algunas posibles soluciones"""
    )



    
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )
