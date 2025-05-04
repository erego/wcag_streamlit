""""
En este módulo gestionaremos la calidad de los datos de los ficheros de la aplicación
y permitiremos hacer correcciones
"""
import os
import streamlit as st
import pandas as pd



st.subheader("Análisis y gestión de calidad de los datos")
st.sidebar.subheader("Calidad de los datos", anchor=False)
st.write(
    """En esta sección veremos algunos posibles problemas
      y se ofreceran algunas posibles soluciones"""
)

@st.cache_data
def get_wcag_data(select_fichero):
    """Lee el fichero excel de accesibilidad a una estructura pandas DataFrame

    Args:
        select_fichero (_type_): Ruta del fichero a seleccionar

    Returns:
        _type_: pandas DataFrame
    """
    data_wcag = pd.read_excel(select_fichero, index_col = 0)
    return data_wcag


PATH_FORMATTED= "./data/formatted/"
lst_ficheros = [PATH_FORMATTED + element for element in os.listdir(PATH_FORMATTED)]
select_fichero = st.selectbox("Elige el fichero con el que trabajar",lst_ficheros,index=None)

if select_fichero:
    data_wcag_subtable = get_wcag_data(select_fichero)
    st.data_editor(data_wcag_subtable, key= "edited_wcag",
                   disabled  = ("Sucess_Criterion", "Principles_Guidelines"))
    st.write(st.session_state["edited_wcag"])

st.data_editor({
	"st.text_area": "widget",
	"st.markdown": "element"
})
