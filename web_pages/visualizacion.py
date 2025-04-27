"""
En este fichero podremos visualizar el dataframe asociado al fichero seleccionado, realizar filtros
y ver diferentes métricas asociadas a dicho dataframe. También visualizaremos sobre un mapa
las ciudades seleccionadas
"""

import os
import sqlite3

import streamlit as st
import pandas as pd

from data_api.data_operations import get_geocode, get_city_data, insert_city_db, get_fichero_db, get_statistics_data
from data_api.wcag_operations import get_config_toml_wcag, get_principles, get_success_criterion, get_guidelines, get_levels_criterion_from_dataframe

st.subheader("Visualización de datos", anchor=False)
st.sidebar.header("Visualización de datos")
st.write(
    """Esta página permite filtrar y visualizar la tabla de WCAG de ayuntamientos"""
)


@st.cache_data
def get_wcag_data(select_fichero):
    data_wcag = pd.read_excel(select_fichero, index_col = 0)
    return data_wcag

@st.cache_data
def get_wcag_cities(select_fichero):
    data_wcag = pd.read_excel(select_fichero)
    cities = data_wcag.columns.values.tolist()[3:]
    cities.sort()
    return cities


if 'versions_wcag' not in st.session_state:
    st.session_state['versions_wcag'] = get_config_toml_wcag()

path_formatted= "./data/formatted/"
lst_ficheros = [path_formatted + element for element in os.listdir(path_formatted)]
select_fichero = st.selectbox("Elige el fichero con el que trabajar",lst_ficheros,index=None)

if select_fichero:

    # Consultamos la mejor versión para el fichero en la base de datos y añadimos las versiones que
    # correspondan
    conn = sqlite3.connect('./data/database/dashboard.db')
    fichero_data = get_fichero_db(select_fichero.split('/')[-1], "formatted", conn)
    conn.close()
    fichero_data = fichero_data[0]
    best_version_fichero = fichero_data[2]
    
    data_wcag_subtable = get_wcag_data(select_fichero)
    configs_wcag = st.session_state['versions_wcag'] 
    versions_wcag = []
    for version_wcag in configs_wcag:

        if float(version_wcag['version']) <= float(best_version_fichero):
            versions_wcag.append(version_wcag['version'])

    index_best = versions_wcag.index(best_version_fichero)

    # Anclamos los desplegables al lateral
    select_wcag_versions = st.sidebar.selectbox("Elige la versión wcag a analizar", versions_wcag, index=index_best)


    if select_wcag_versions:
        principles_version = get_principles(select_wcag_versions, configs_wcag)
        select_principles = st.sidebar.multiselect("Elige los principios", principles_version,)
    
        guidelines_version = get_guidelines(select_wcag_versions, configs_wcag)

        if select_principles:
            lst_num_principles = []
            for select_principle in select_principles:
                lst_num_principles.append(select_principle[10:11])
           
            guidelines_version = [element for element in guidelines_version if element.startswith(tuple(lst_num_principles))]

        select_guidelines = st.sidebar.multiselect("Elige las pautas principales", guidelines_version,)


    if select_wcag_versions and select_wcag_versions !=best_version_fichero:
        criterions_version = get_success_criterion(select_wcag_versions, configs_wcag )
        criterions_version_index = [item.split()[0] for item in criterions_version]
        criterions_best = get_success_criterion(best_version_fichero, configs_wcag)
        criterions_best_index = [item.split()[0] for item in criterions_best]
        criterions_to_filter_index = [item for item in criterions_best_index if item not in criterions_version_index] 
        criterions_to_filter = [item for item in criterions_best if item.split()[0] in criterions_to_filter_index]

        data_wcag_subtable = data_wcag_subtable[~data_wcag_subtable['Principles_Guidelines'].isin(criterions_to_filter)]
   

    if select_guidelines:
        lst_to_filter = []
        for select_guideline in select_guidelines:
            lst_to_filter.append(select_guideline.split()[0])
            lst_to_filter.append("Principle " + select_guideline[0])
        
        lst_to_filter = set(lst_to_filter)
        result = data_wcag_subtable.loc[:, 'Principles_Guidelines'].astype(str).str.startswith(tuple(lst_to_filter))
        data_wcag_subtable = data_wcag_subtable[result]

    elif select_principles:
        lst_to_filter = []
        # Número del principio elegido
        for select_principle in select_principles:
            lst_to_filter.append(select_principle)
            lst_to_filter.append(select_principle[10:11])
        lst_to_filter = set(lst_to_filter)

        result = data_wcag_subtable.loc[:, 'Principles_Guidelines'].astype(str).str.startswith(tuple(lst_to_filter))
        data_wcag_subtable = data_wcag_subtable[result]


    levels_criterion = get_levels_criterion_from_dataframe(data_wcag_subtable)
    select_levels = st.sidebar.multiselect("Elige los niveles", levels_criterion,)


    if select_levels:

        lst_levels_filter = select_levels

        data_wcag_subtable = data_wcag_subtable[data_wcag_subtable['Sucess_Criterion'].isin(lst_levels_filter) | data_wcag_subtable['Sucess_Criterion'].isnull()]


    all_cities = get_wcag_cities(select_fichero)
    select_cities = st.sidebar.multiselect(
        "Elige las ciudades", all_cities, 
    )

    if select_cities:
        data_wcag_subtable = data_wcag_subtable.loc[:,["Sucess_Criterion", "Principles_Guidelines"] + select_cities]
        selected_cities = select_cities
    else:
        selected_cities = all_cities

    selected_lats = []
    selected_lons = []
    conn = sqlite3.connect('./data/database/dashboard.db')  

    for city in selected_cities:
      
        # Comprobamos si la ciudad está en la base de datos y si no llamamos al api
        result_db = get_city_data(city, conn)

        if len(result_db) ==1 :
            lat = result_db[0][0]
            lon = result_db[0][1]
            status = result_db[0][2]    
        else:
            data = get_geocode(city)
            
            if data is None:
                lat = 0
                lon = 0
                status = False
            else:
                lat = data["lat"]
                lon = data["lng"]
                status = True

            # Insertamos en la base de datos porque no existe
            insert_city_db(city, lat, lon, status, conn)

        selected_lats.append(lat)
        selected_lons.append(lon)       

    conn.close()


    st.dataframe(data_wcag_subtable)

    st.markdown("# Informe de calidad de los datos")
    st.write(
        """Esta sección permite visualizar caraterísticas de los datos """
    )

    data_wcag_subtable_statistics = get_statistics_data(data_wcag_subtable)
    st.dataframe(data_wcag_subtable_statistics) 

    data_stacked = data_wcag_subtable.copy()
    data_stacked = data_stacked.dropna() 
    data_stacked.drop('Sucess_Criterion', axis=1, inplace=True) 
    data_stacked.set_index('Principles_Guidelines', inplace=True)

    list_rows = []
    for index, value in data_stacked.iterrows():
      series_valor = value.value_counts().sort_index()
      row_dict = dict()
      row_dict["Principles_Guidelines"]=index
      row_dict["Valor 1"] =series_valor.at[1.0] if 1.0 in series_valor.index  else 0
      row_dict["Valor 2"] =series_valor.at[2.0] if 2.0 in series_valor.index  else 0
      row_dict["Valor 3"] =series_valor.at[3.0] if 3.0 in series_valor.index  else 0
      row_dict["Valor 4"] =series_valor.at[4.0] if 4.0 in series_valor.index  else 0
      row_dict["Valor 5"] =series_valor.at[5.0] if 5.0 in series_valor.index  else 0
      list_rows.append(row_dict)

    data_stacked = pd.DataFrame(list_rows)
    data_stacked.set_index('Principles_Guidelines', inplace=True)
    st.bar_chart(data_stacked)
  
    st.bar_chart(data_wcag_subtable_statistics, y=["Valor máximo"], color=["#d2c5dc"],)
    st.bar_chart(data_wcag_subtable_statistics, y=["Valor mínimo"], color=["#e5e0b7"],)
    st.bar_chart(data_wcag_subtable_statistics, y=["Cardinalidad"], color=["#f9dfd6"],)

    dataframe_geo = pd.DataFrame({
        'ciudad' : selected_cities,
        'lat': selected_lats,
        'lon': selected_lons })

    import pydeck as pdk
    st.pydeck_chart(
        pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=40.41,
                longitude=-3.70,
                zoom=4,
            ),
            layers=[

                pdk.Layer(
                    "ScatterplotLayer",
                    data=dataframe_geo,
                    get_position="[lon, lat]",
                    get_color="[100, 30, 0, 160]",
                    pickable=True,
                    get_radius=15000,
                ),
            ],
            tooltip={"text": "{ciudad}"},
        )
    )
