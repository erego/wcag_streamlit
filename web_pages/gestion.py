import streamlit as st
import os
import pathlib
import pandas as pd
import tomllib

#st.set_page_config(page_title="Gestión de ficheros", page_icon=":file", layout="wide")
st.markdown("## Gestión de ficheros")
st.sidebar.header("Gestión de ficheros")

# Obtener las configuraciones de las versiones wcag soportadas
@st.cache_resource
def get_config_toml_wcag():
    with open('custom.toml', 'rb') as file:
        config = tomllib.load(file)
        versions_wcag = config['wcag']
    return versions_wcag

upload_file = st.file_uploader("Elige un fichero para subirlo a la aplicación")

if upload_file is not None:

    with open(os.path.join("./data/raw/",upload_file.name),"wb") as f: 
          f.write(upload_file.getbuffer())  

    st.success("Fichero Almacenado")

col1, col2 = st.columns(2)

path_raw= "./data/raw/"
path_formatted= "./data/formatted/"


def form_callback():
    for index, element in enumerate(os.listdir(path_raw)):
        name = 'dynamic_checkbox_raw_' + str(index)

        if st.session_state[name] is True:
            os.unlink(path_raw + element)
            st.write( f"Borrado fichero {path_raw + element }")          


    for index, element in enumerate(os.listdir(path_formatted)):
        name = 'dynamic_checkbox_formatted_' + str(index)

        if st.session_state[name] is True:
            os.unlink(path_formatted + element)
            st.write( f"Borrado fichero {path_formatted + element }")


with col1:
        st.header("Ficheros en bruto")
        for index, element in enumerate(os.listdir(path_raw)):
            st.checkbox(path_raw + element, key='dynamic_checkbox_raw_' + str(index))

with col2:
    st.header("Ficheros saneados")
    for index, element in enumerate(os.listdir(path_formatted)):
        st.checkbox(path_formatted + element, key='dynamic_checkbox_formatted_' + str(index))
            

with st.form("form_delete"):
      

    delete_button = st.form_submit_button("Borra los ficheros seleccionados", on_click=form_callback)



configs_wcag = get_config_toml_wcag()
versions_wcag = []
for version_wcag in configs_wcag:
    versions_wcag.append(version_wcag['version'])


def get_principles(version_wcag, configs_wcag):
    filtered_principles = [config_wcag['principles'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return filtered_principles


def get_guidelines(version_wcag, configs_wcag):
    filtered_guidelines = [config_wcag['guidelines'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return filtered_guidelines

def get_success_criterion(version_wcag, configs_wcag):
    filtered_success_criterion = [config_wcag['success_criterion'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return filtered_success_criterion



with st.form("form_limpieza"):
    st.header("Limpieza inicial")
    st.markdown(
        """
        En esta sección se puede hacer una limpieza inicial básica de los datos en bruto del fichero seleccionado, teniendo en cuenta el formato en el que llega.
       
        
        """

    )
    st.markdown("Tras pulsar el botón de limpieza, el fichero se almacenará en los ficheros formateados")
    st.markdown("Los pasos de limpieza que se realizan son los siguientes:")
    st.markdown("""
        - Se borrar las dos últimas columnas del fichero, ya que son iguales a las primeras
        - Se eliminan las filas que son todo NA(filas en blanco), ya que no aportan valor
        - Se renombran las primeras dos columnas vacías por otros nombres más significativos como son: Sucess_Criterion y Principles_Guidelines
        - Se incluyen las guidelines  en las filas del dataframe pues no vienen incluidas

    """)


    path_raw= "./data/raw/"

    lst_ficheros = [path_raw + element for element in os.listdir(path_raw)]

    select_fichero = st.selectbox("Elige el fichero con el que trabajar",lst_ficheros,index=None)


    # Anclamos los desplegables al lateral
    select_wcag_versions = st.selectbox("Elige la versión wcag", versions_wcag)

     
    clean_button = st.form_submit_button("Realiza la limpieza")


if clean_button:
    
    data_wcag = pd.read_excel(select_fichero)

    num_columns = data_wcag.shape[1]
    
    # Borramos las dos últimas columnas pues son iguales a las dos primeras
    data_wcag.drop(columns=[data_wcag.columns[num_columns-1],data_wcag.columns[num_columns-2]], inplace = True)

    # Eliminamos las filas que son todo NA(filas en blanco)
    data_wcag.dropna(how='all', inplace=True)
    data_wcag.reset_index(drop=True, inplace=True)

    # Renombramos las primeras dos columnas vacías por otros nombres más significativos
    data_wcag.rename(columns = {data_wcag.columns[0]: 'Sucess_Criterion', data_wcag.columns[1]: 'Principles_Guidelines'}, inplace=True)

    cities = data_wcag.columns.values.tolist()[2:]
    
    
    principles = get_principles(select_wcag_versions, configs_wcag)

    guidelines = get_guidelines(select_wcag_versions, configs_wcag)

    success_criterion = get_success_criterion(select_wcag_versions, configs_wcag)
    
    # Vamos a insertar las guidelines en el dataframe original que no estaban incluidas

    for guideline in guidelines:

        text_to_find = guideline[0:3]

        result = data_wcag.loc[:, 'Principles_Guidelines'].astype(str).str.startswith(text_to_find)
        result = result.loc[result]
        index_found=result.idxmin()

        row_to_add = pd.DataFrame({"Principles_Guidelines": guideline}, index=[index_found])
        data_wcag = pd.concat([data_wcag.iloc[:index_found], row_to_add, data_wcag.iloc[index_found:]]).reset_index(drop=True)
    
    path = pathlib.Path(select_fichero)

    new_name = path.stem + "_formatted" + path.suffix

    path_output = pathlib.Path(path.parent.parent).joinpath('formatted', new_name)

    
    data_wcag.to_excel(path_output)


