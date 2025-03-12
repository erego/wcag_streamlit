import streamlit as st
import os


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

with st.form("form_delete"):
    
    with col1:
        st.header("Ficheros en bruto")
        for index, element in enumerate(os.listdir(path_raw)):
            st.checkbox(path_raw + element, key='dynamic_checkbox_raw_' + str(index))

    with col2:
        st.header("Ficheros saneados")
        for index, element in enumerate(os.listdir(path_formatted)):
            st.checkbox(path_formatted + element, key='dynamic_checkbox_formatted_' + str(index))



    delete_button = st.form_submit_button("Borra los ficheros seleccionados", on_click=form_callback)

    
