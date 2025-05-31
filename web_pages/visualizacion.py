"""
En este fichero podremos visualizar el dataframe asociado al fichero seleccionado, realizar filtros
y ver diferentes métricas asociadas a dicho dataframe. También visualizaremos sobre un mapa
las localizaciones seleccionadas
"""

import os
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

from data_api.data_operations import get_geocode, get_location_data, insert_location_db, get_fichero_db
from data_api.data_operations import get_statistics_data
from data_api.wcag_operations import get_config_toml_wcag, get_principles, get_success_criterion
from data_api.wcag_operations import get_guidelines, get_levels_criterion_from_dataframe

st.subheader("Visualización de datos", anchor=False)
st.sidebar.header("Visualización de datos")
st.write(
    """Esta página permite filtrar y visualizar la tabla de WCAG de ayuntamientos"""
)

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

if 'versions_wcag' not in st.session_state:
    st.session_state['versions_wcag'] = get_config_toml_wcag()

PATH_FORMATTED= "./data/formatted/"
lst_ficheros = [PATH_FORMATTED + element for element in os.listdir(PATH_FORMATTED)]
select_fichero = st.selectbox("Elige el fichero con el que trabajar",lst_ficheros,index=None)

if select_fichero:

    # Consultamos la mejor versión para el fichero en la base de datos y añadimos las versiones que
    # correspondan
    conn = sqlite3.connect(st.secrets.db_production.path)
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
    select_wcag_versions = st.sidebar.selectbox("Elige la versión wcag a analizar",
                                                versions_wcag, index=index_best)
    if select_wcag_versions:
        principles_version = get_principles(select_wcag_versions, configs_wcag)
        select_principles = st.sidebar.multiselect("Elige los principios", principles_version,)
        guidelines_version = get_guidelines(select_wcag_versions, configs_wcag)

        if select_principles:
            lst_num_principles =[]
            for select_principle in select_principles:
                lst_num_principles.append(select_principle[10:11])
            guidelines_version = [element for element in guidelines_version
                                  if element.startswith(tuple(lst_num_principles))]
        select_guidelines = st.sidebar.multiselect("Elige las pautas principales",
                                                   guidelines_version,)

    if select_wcag_versions and select_wcag_versions !=best_version_fichero:
        criterions_version = get_success_criterion(select_wcag_versions, configs_wcag )
        criterions_version_index = [item.split()[0] for item in criterions_version]
        criterions_best = get_success_criterion(best_version_fichero, configs_wcag)
        criterions_best_index = [item.split()[0] for item in criterions_best]
        criterions_to_filter_index = [item for item in criterions_best_index if item
                                      not in criterions_version_index] 
        criterions_to_filter = [item for item in criterions_best if item.split()[0]
                                in criterions_to_filter_index]

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


    all_locations = get_wcag_locations(select_fichero)
    select_locations = st.sidebar.multiselect(
        "Elige las localizaciones", all_locations, 
    )

    if select_locations:
        data_wcag_subtable = data_wcag_subtable.loc[:,["Sucess_Criterion",
                                                       "Principles_Guidelines"] + select_locations]
        selected_locations = select_locations
    else:
        selected_locations = all_locations

    selected_lats = []
    selected_lons = []
    conn = sqlite3.connect(st.secrets.db_production.path)

    for location in selected_locations:
        # Comprobamos si la localización está en la base de datos y si no llamamos al api
        result_db = get_location_data(location, conn)
        if len(result_db) ==1 :
            lat = result_db[0][0]
            lon = result_db[0][1]
            status = result_db[0][2]
        else:
            data = get_geocode(location)
            if data is None:
                lat = 0
                lon = 0
                status = False
            else:
                lat = data["lat"]
                lon = data["lng"]
                status = True

            # Insertamos en la base de datos porque no existe
            insert_location_db(location, lat, lon, status, conn)

        selected_lats.append(lat)
        selected_lons.append(lon)

    conn.close()


    st.dataframe(data_wcag_subtable)

    st.markdown("# Informe de los datos")
    st.write(
        """Esta sección permite visualizar caraterísticas de los datos """
    )

    data_wcag_subtable_statistics = get_statistics_data(data_wcag_subtable)
    st.dataframe(data_wcag_subtable_statistics.style.format({"Media": "{:.2f}", "Mediana": "{:.0f}", 
                                                             "Desviación Estándar": "{:.2f}", "Valor máximo": "{:.0f}","Valor mínimo": "{:.0f}"}))
    
    data_stacked = data_wcag_subtable.copy()
    data_stacked = data_stacked.dropna()
    data_stacked.drop('Sucess_Criterion', axis=1, inplace=True)
    data_stacked.set_index('Principles_Guidelines', inplace=True)

    max_range_likert = data_stacked.max().max()

    if max_range_likert == 5:
        select_likert = st.sidebar.selectbox("Elige la escala Likert a visualizar",["De 5 puntos", "De 3 puntos"],index=0)
    else:
        select_likert = st.sidebar.selectbox("Elige la escala Likert a visualizar",["De 3 puntos"],index=0)

    list_rows = []
    
    for index, value in data_stacked.iterrows():
        series_valor = value.value_counts().sort_index()
        row_dict = {}
        row_dict["Principles_Guidelines"]=index
        if select_likert and select_likert == "De 3 puntos":
            result_1= series_valor.at[1.0] if 1.0 in series_valor.index  else 0
            result_2= series_valor.at[2.0] if 2.0 in series_valor.index  else 0
            row_dict["1: No conseguido"] = result_1 + result_2
        else:
            row_dict["1: No conseguido"] = series_valor.at[1.0] if 1.0 in series_valor.index  else 0
            row_dict["2: Parcialmente conseguido"] = series_valor.at[2.0] if 2.0 in series_valor.index  else 0
        if select_likert and select_likert == "De 3 puntos":
            row_dict["2: No aplicable"] = series_valor.at[3.0] if 3.0 in series_valor.index  else 0
        else:
            row_dict["3: No aplicable"] = series_valor.at[3.0] if 3.0 in series_valor.index  else 0
        if select_likert and select_likert == "De 3 puntos":
            result_4= series_valor.at[4.0] if 4.0 in series_valor.index  else 0
            result_5= series_valor.at[5.0] if 5.0 in series_valor.index  else 0
            row_dict["3: Totalmente conseguido"] = result_4 + result_5
        else:
            row_dict["4: Ampliamente conseguido"] = series_valor.at[4.0] if 4.0 in series_valor.index  else 0
            row_dict["5: Totalmente conseguido"] = series_valor.at[5.0] if 5.0 in series_valor.index  else 0
        list_rows.append(row_dict)

    data_stacked = pd.DataFrame(list_rows)
    
    data_stacked.set_index('Principles_Guidelines', inplace=True)

    suma_total = data_stacked.sum(axis=1)
    suma_total.name = 'Total valores'
    data_stacked_percentage = pd.concat([data_stacked, suma_total], axis = 1)
    if select_likert and select_likert == "De 3 puntos":
        data_stacked_percentage.insert(1,"% NC", (data_stacked_percentage["1: No conseguido"] * 100)/data_stacked_percentage["Total valores"]) 
        data_stacked_percentage.insert(3,"% NA", (data_stacked_percentage["2: No aplicable"] * 100)/data_stacked_percentage["Total valores"]) 
        data_stacked_percentage.insert(5,"% TC", (data_stacked_percentage["3: Totalmente conseguido"] * 100)/data_stacked_percentage["Total valores"]) 
    else:
        data_stacked_percentage.insert(1,"% NC", (data_stacked_percentage["1: No conseguido"] * 100)/data_stacked_percentage["Total valores"]) 
        data_stacked_percentage.insert(3,"% PC", (data_stacked_percentage["2: Parcialmente conseguido"] * 100)/data_stacked_percentage["Total valores"]) 
        data_stacked_percentage.insert(5,"% NA", (data_stacked_percentage["3: No aplicable"] * 100)/data_stacked_percentage["Total valores"])      
        data_stacked_percentage.insert(7,"% AC", (data_stacked_percentage["4: Ampliamente conseguido"] * 100)/data_stacked_percentage["Total valores"]) 
        data_stacked_percentage.insert(9,"% TC", (data_stacked_percentage["5: Totalmente conseguido"] * 100)/data_stacked_percentage["Total valores"])

    if select_likert and select_likert == "De 3 puntos":
        st.dataframe(data_stacked_percentage.style.format({"% NC": "{:.2f}", "% NA": "{:.20f}", 
                                                             "% TC": "{:.2f}"}) )
    else:         
        st.dataframe(data_stacked_percentage.style.format({"% NC": "{:.2f}","% PC": "{:.2f}", "% NA": "{:.2f}", 
                                                              "% AC": "{:.2f}","% TC": "{:.2f}"}))

    # Creación del gráfico altair
    data_stacked = data_stacked.melt(var_name="likert_scale", ignore_index=False)
    if select_likert and select_likert == "De 3 puntos":
        colors = ['#A6C8FF','#4B8BBE',"#8B6D5E"]
    else:
        colors = ['#A6C8FF','#4B8BBE',"#8B6D5E","#FFFF7E",'#FF9900']
    chart = alt.Chart(data_stacked.reset_index()).mark_bar().encode(
    x='Principles_Guidelines:N',
    y='sum(value):Q',
    color=alt.Color('likert_scale:N'),
    ).properties(
    height=400
    ).configure_range(
    category=alt.RangeScheme(colors)
)

    st.altair_chart(chart, theme=None, use_container_width=True)

    #st.bar_chart(data_stacked, color=None)
    #st.bar_chart(data_wcag_subtable_statistics, y=["Valor máximo"], color=["#d2c5dc"],)
    chart=alt.Chart(data_wcag_subtable_statistics.reset_index()).mark_bar().encode(
        x='index', y="Valor máximo", tooltip=['index', 'Mejores localizaciones']).configure_mark(
            color='#d2c5dc')
    
    st.altair_chart(chart, theme=None, use_container_width=True)
    #st.bar_chart(data_wcag_subtable_statistics, y=["Valor mínimo"], color=["#e5e0b7"],)

    chart=alt.Chart(data_wcag_subtable_statistics.reset_index()).mark_bar().encode(
        x='index', y="Valor mínimo", tooltip=['index', 'Peores localizaciones']).configure_mark(
            color='#e5e0b7')
    st.altair_chart(chart, theme=None, use_container_width=True)

    #st.bar_chart(data_wcag_subtable_statistics, y=["Cardinalidad"], color=["#f9dfd6"],)

    chart=alt.Chart(data_wcag_subtable_statistics.reset_index()).mark_bar().encode(
        x='index', y="Cardinalidad", tooltip=['index']).configure_mark(
            color='#f9dfd6')
    st.altair_chart(chart, theme=None, use_container_width=True)

    dataframe_geo = pd.DataFrame({
        'location' : selected_locations,
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
            tooltip={"text": "{location}"},
        )
    )
