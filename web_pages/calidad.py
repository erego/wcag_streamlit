""""
En este módulo gestionaremos la calidad de los datos de los ficheros de la aplicación
y permitiremos hacer correcciones
"""
import os
import sqlite3
import streamlit as st
import pandas as pd

from data_api.data_operations import get_geocode, get_location_data

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


def get_wcag_locations(select_fichero):
    """Obtiene el listado de localizaciones de un fichero de accesibilidad

    Args:
        select_fichero (_type_): Ruta del fichero a leer

    Returns:
        _type_: Lista de las localizaciones que lo componen
    """
    data_wcag = pd.read_excel(select_fichero)
    locations = data_wcag.columns.values.tolist()[3:]
    locations.sort()
    return locations

def form_callback_modify_location():
    """Callback al pulsar el modificar la localización
    """

    if st.session_state["select_localizacion"] and st.session_state["localizacion_modified"]:
 
        # Modificamos el valor en la base de datos
        location=st.session_state["localizacion_modified"]

        data_to_insert = get_geocode(location)
        status =  True
        if data_to_insert is None:
            lat = 0.0
            lon = 0.0
            status =  False
        else:
            lat = data_to_insert["lat"]
            lon = data_to_insert["lng"]


        if status is False:
            with container_update_location:
                st.warning("La nueva descripción no da un valor geográfico válido")

        else:
            
            conn = sqlite3.connect(st.secrets.db_production.path)
            cur = conn.cursor()
            cur.execute("UPDATE localizaciones SET descripcion = :location, latitud = :lat, longitud = :lon, status = :status WHERE descripcion = :old_description",
                        {'location':location, 'lat': lat, 'lon': lon, 'old_description': st.session_state["select_localizacion"], 'status': status})

            conn.commit()
            cur.close()
            
            with container_update_location:
                st.info("Valor modificado correctamente")

        # Modificamos el valor en la base de datos el valor en el excel
        data_wcag_subtable = get_wcag_data(select_fichero)
        data_wcag_subtable.rename(columns={st.session_state["select_localizacion"]: st.session_state["localizacion_modified"]}, inplace=True)
        data_wcag_subtable.to_excel(select_fichero)
    else:
        with container_update_location:
            st.warning("Debe seleccionar La localización a modificar y agregar la nueva descripción")

PATH_FORMATTED= "./data/formatted/"
lst_ficheros = [PATH_FORMATTED + element for element in os.listdir(PATH_FORMATTED)]
select_fichero = st.selectbox("Elige el fichero con el que trabajar",lst_ficheros,index=None)

st.divider()

st.subheader("Modificación de localizaciones", anchor=False)
st.markdown(
"""
        En esta sección se puede modificar los nombres de
        las localizaciones con problemas y almacenarlos.
        Los valores con error aparecerán en la lista desplegable
"""
)

if select_fichero:
    with st.form("form_update_locations", border=False):
        conn = sqlite3.connect(st.secrets.db_production.path)
        cur = conn.cursor()
        cur.execute("SELECT descripcion FROM localizaciones where status=0")
        all_locations = get_wcag_locations(select_fichero)
        results = cur.fetchall()
        result_list = [result[0] for result in results]
        cur.close()
        conn.close()
        col1, col2 = st.columns(2)
        list_to_modify = [element for element in result_list if element in all_locations]    
        with col1:           
            st.selectbox("Elige la localizacion a modificar",list_to_modify, key="select_localizacion",index=None)
        with col2:
            st.text_input('Introduce el nuevo valor', key="localizacion_modified")
        update_locations_button = st.form_submit_button("Realiza la modificación",
                                          on_click=form_callback_modify_location)
        container_update_location = st.container()

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
