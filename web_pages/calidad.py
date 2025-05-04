""""
En este módulo gestionaremos la calidad de los datos de los ficheros de la aplicación
y permitiremos hacer correcciones
"""
import os
import sqlite3
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


def get_wcag_cities(select_fichero):
    """Obtiene el listado de ciudades de un fichero de accesibilidad

    Args:
        select_fichero (_type_): Ruta del fichero a leer

    Returns:
        _type_: Lista de las ciudades que lo componen
    """
    data_wcag = pd.read_excel(select_fichero)
    cities = data_wcag.columns.values.tolist()[3:]
    cities.sort()
    return cities


PATH_FORMATTED= "./data/formatted/"
lst_ficheros = [PATH_FORMATTED + element for element in os.listdir(PATH_FORMATTED)]
select_fichero = st.selectbox("Elige el fichero con el que trabajar",lst_ficheros,index=None)

st.divider()

st.subheader("Modificación de ciudades", anchor=False)
st.markdown(
"""
        En esta sección se puede modificar los nombres de
        las ciudades con problemas y almacenarlos.
"""
)

if select_fichero:
    with st.form("form_update_cities", border=False):
        conn = sqlite3.connect(st.secrets.db_production.path)
        cur = conn.cursor()
        cur.execute("SELECT ciudad FROM ciudades where status=0")
        all_cities = get_wcag_cities(select_fichero)
        results = cur.fetchall()
        result_list = [result[0] for result in results]
        cur.close()
        conn.close()

        list_to_modify = [element for element in result_list if element in all_cities]

        st.write(list_to_modify)

        update_cities_button = st.form_submit_button("Realiza la modificación")

st.divider()

st.subheader("Modificación del dataframe", anchor=False)
st.markdown(
"""
        En esta sección se puede modificar los distintos valores del
        dataframe y almacenarlos.
"""
)


if select_fichero:
    with st.form("form_update_dataframe", border=False):
        data_wcag_subtable = get_wcag_data(select_fichero)
        df_edited= st.data_editor(data_wcag_subtable, key= "edited_wcag",
                    disabled  = ("_index","Sucess_Criterion", "Principles_Guidelines"))

        update_dataframe_button = st.form_submit_button("Realiza la modificación")

    if update_dataframe_button:
        get_wcag_data.clear()
        df_edited.to_excel(select_fichero)
