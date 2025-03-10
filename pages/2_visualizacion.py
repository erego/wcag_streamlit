import streamlit as st
import pandas as pd
import tomllib

import altair as alt
import urllib
import requests
import json

st.set_page_config(page_title="Visualización de datos", page_icon="📊", layout="wide")

st.markdown("# Visualización de datos")
st.sidebar.header("Visualización de datos")
st.write(
    """Esta página permite filtrar y visualizar la tabla de WCAG de ayuntamientos"""
)


# Obtener las configuraciones de las versiones wcag soportadas
@st.cache_resource
def get_config_toml_wcag():
    with open('custom.toml', 'rb') as file:
        config = tomllib.load(file)
        versions_wcag = config['wcag']
    return versions_wcag


@st.cache_data
def get_wcag_data():
    data_wcag = pd.read_excel("../../data/WCAG_ayuntamientos_formatted.xlsx", index_col = 0)
    return data_wcag

@st.cache_data
def get_wcag_cities():
    data_wcag = pd.read_excel("../../data/WCAG_ayuntamientos_formatted.xlsx")
    cities = data_wcag.columns.values.tolist()[3:]
    cities.sort()
    return cities

@st.cache_data
def get_geocode(ciudad:str):
    ciudad = urllib.parse.quote(ciudad)
    url = f'http://www.cartociudad.es/geocoder/api/geocoder/findJsonp?q={ciudad}'
    r = requests.get(url)
    result = r.text.replace('callback(', '')[:-1]
    result = json.loads(result)
    #print(result)
    return result or None


def get_statistics_data(data_wcag_subtable):
    # Nos quedaremos sólo con las columnas que tengan criterios de éxito y borraremos el resto
    data_wcag_subtable_statistics =  data_wcag_subtable.set_index('Principles_Guidelines')
    data_wcag_subtable_statistics = data_wcag_subtable_statistics.dropna(subset=['Sucess_Criterion'])
    data_wcag_subtable_statistics = data_wcag_subtable_statistics.transpose()
    data_wcag_subtable_statistics.drop('Sucess_Criterion', inplace = True)

    max_serie = data_wcag_subtable_statistics.max(axis = 0)
    max_serie.name = 'Valor máximo'

    min_serie = data_wcag_subtable_statistics.min(axis = 0)
    min_serie.name = 'Valor mínimo'


    total_valores_serie = data_wcag_subtable_statistics.count(axis = 0)
    total_valores_serie.name = 'Total Valores'

    valores_nulos_serie = data_wcag_subtable_statistics.isnull().sum()
    valores_nulos_serie.name = 'Total valores nulos'

    cardinalidad_serie = data_wcag_subtable_statistics.nunique()
    cardinalidad_serie.name = 'Cardinalidad'

    moda_serie = data_wcag_subtable_statistics.mode(axis = 0).transpose().fillna('').astype(str).apply(','.join, axis=1)
    moda_serie.name = 'Moda'

    result_statistics = pd.concat([total_valores_serie, max_serie, min_serie, valores_nulos_serie, cardinalidad_serie, moda_serie], axis = 1)
     
    return result_statistics

def get_principles(version_wcag, configs_wcag):
    filtered_principles = [config_wcag['principles'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return filtered_principles
    
   
data_wcag_subtable = get_wcag_data()

configs_wcag = get_config_toml_wcag()
versions_wcag = []
for version_wcag in configs_wcag:
    versions_wcag.append(version_wcag['version'])

# Anclamos los desplegables al lateral
select_wcag_versions = st.sidebar.selectbox("Elige la versión wcag a analizar", versions_wcag)


if select_wcag_versions:
    principles_version = get_principles(select_wcag_versions, configs_wcag)
    select_principles = st.sidebar.multiselect("Elige los principios", principles_version,)

all_cities = get_wcag_cities()
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

for city in selected_cities:
    data = get_geocode(city)
    if data is None:
        selected_lats.append(0)
        selected_lons.append(0)
    else:
        selected_lats.append(data["lat"])
        selected_lons.append(data["lng"])

if select_principles:
    # Número del principio elegido
    lst_num_principles = []
    for select_principle in select_principles:
        lst_num_principles.append(select_principle)
        lst_num_principles.append(select_principle[10:11])


    result = data_wcag_subtable.loc[:, 'Principles_Guidelines'].astype(str).str.startswith(tuple(lst_num_principles))
    data_wcag_subtable = data_wcag_subtable[result]
   
st.dataframe(data_wcag_subtable)


st.markdown("# Informe de calidad de los datos")
st.write(
    """Esta sección permite visualizar caraterísticas de los datos """
)

data_wcag_subtable_statistics = get_statistics_data(data_wcag_subtable)

st.dataframe(data_wcag_subtable_statistics) 

st.bar_chart(
    data_wcag_subtable_statistics,
    y=["Valor máximo"],
    color=["#d2c5dc"],  
)
st.bar_chart(
    data_wcag_subtable_statistics,
    y=["Valor mínimo"],
    color=["#e5e0b7"],  
)
st.bar_chart(
    data_wcag_subtable_statistics,
    y=["Cardinalidad"],
    color=["#f9dfd6"],  
)


dataframe_geo = pd.DataFrame({
    'ciudad' : selected_cities,
    'lat': selected_lats,
    'lon': selected_lons })

#st.map(dataframe_geo, size = 50)

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
                get_radius=15000,
            ),
        ],
    )
)





