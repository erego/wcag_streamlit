import urllib
import requests
import json

import pandas as pd

def get_statistics_data(data_wcag_subtable):
    """Obtiene diferentes valores estadísticos en formato DataFrame de un DataFrame proporcionado

    Args:
        data_wcag_subtable (_type_): DataFrame del que obtendremos las estadísticas

    Returns:
        _type_: Devuelve un DataFrame con valores asociados estadísticos asociados al DataFrame proporcionado
    """
    # Nos quedaremos sólo con las columnas que tengan criterios de éxito y borraremos el resto
    data_wcag_subtable_statistics =  data_wcag_subtable.set_index('Principles_Guidelines')
    data_wcag_subtable_statistics = data_wcag_subtable_statistics.dropna(
        subset=['Sucess_Criterion'])
    data_wcag_subtable_statistics = data_wcag_subtable_statistics.transpose()
    data_wcag_subtable_statistics.drop('Sucess_Criterion', inplace = True)

    max_serie = data_wcag_subtable_statistics.max(axis = 0)
    min_serie = data_wcag_subtable_statistics.min(axis = 0)

    dict_max_locations = dict()
    for index, value in max_serie.items():
        result_column = data_wcag_subtable_statistics.loc[:,index]
        result_column = result_column[result_column == value].index.tolist()
        result_column.sort()
        dict_max_locations[index] = result_column


    dict_min_locations = dict()
    for index, value in min_serie.items():
        result_column = data_wcag_subtable_statistics.loc[:,index]
        result_column = result_column[result_column == value].index.tolist()
        result_column.sort()
        dict_min_locations[index] = result_column


    max_serie_locations = pd.Series(dict_max_locations)
    max_serie_locations.name = 'Mejores localizaciones'
    max_serie.name = 'Valor máximo'
    min_serie_locations = pd.Series(dict_min_locations)
    min_serie_locations.name = 'Peores localizaciones'
    min_serie.name = 'Valor mínimo'
    total_valores_serie = data_wcag_subtable_statistics.count(axis = 0)
    total_valores_serie.name = 'Total Valores'
    valores_nulos_serie = data_wcag_subtable_statistics.isnull().sum()
    valores_nulos_serie.name = 'Total valores nulos'
    cardinalidad_serie = data_wcag_subtable_statistics.nunique()
    cardinalidad_serie.name = 'Cardinalidad'
    #moda_serie = data_wcag_subtable_statistics.mode(axis = 0).transpose(
    #    ).fillna('').astype(str).apply(','.join, axis=1)
    #moda_serie.name = 'Moda'
    mean_serie = data_wcag_subtable_statistics.mean(axis = 0)
    mean_serie.name = 'Media'
    median_serie = data_wcag_subtable_statistics.median(axis = 0)
    median_serie.name = 'Mediana'
    std_serie = data_wcag_subtable_statistics.std(axis = 0)
    std_serie.name = 'Desviación Estándar'
    result_statistics = pd.concat([total_valores_serie, valores_nulos_serie, 
                                   cardinalidad_serie, mean_serie, median_serie, std_serie, max_serie_locations, max_serie,
                                    min_serie_locations, min_serie], axis = 1) 
    return result_statistics

def get_geocode(localizacion:str):
    """Llamada a la api de cartociudad para obtener datos geográficos de la localización

    Args:
        location (str): Nombre de la localización a buscar

    Returns:
       python dictionary: Diccionario de python con los datos geográficos de la localización
    """
    localizacion = urllib.parse.quote(localizacion)
    url = f'http://www.cartociudad.es/geocoder/api/geocoder/findJsonp?q={localizacion}'
    r = requests.get(url)
    result = r.text.replace('callback(', '')[:-1]
    try:
        result = json.loads(result)
        return result or None
    except json.JSONDecodeError as error:
        print(error)
        return None

def get_location_data(location: str, connection):

    """Obtiene los datos de una localización de la base de datos

    Returns:
        list: Los datos de la base de datos para la localización solicitada
    """
   
    cur = connection.cursor()
    cur.execute("SELECT latitud, longitud, status FROM localizaciones where descripcion = :location", {'location':location})
    result = cur.fetchall()
    cur.close()
    return result

def get_fichero_db(nombre:str, tipo:str, connection):
    """Obtiene los datos de un fichero de la base de datos

    Args:
        nombre (str): Nombre del fichero
        tipo (str): Tipo (si está en bruto o formateado)
        connection (_type_): Conexión a la base de datos
    """
    cur = connection.cursor()
    cur.execute("SELECT nombre, tipo, mejor_version FROM ficheros where nombre = :name and tipo = :type", {'name':nombre, 'type': tipo})
    result = cur.fetchall()
    cur.close()
    return result

def insert_fichero_db(nombre:str, tipo:str, mejor_version:str, connection):
    """Inserta un registro en la tabla ficheros

    Args:
        nombre (str): Nombre del fichero
        tipo (str): Tipo (si está en bruto o formateado)
        mejor_version (str): Mejor versión de wcag que cumple el fichero
        connection (_type_): Conexión a la base de datos
    """

    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ficheros (nombre TEXT, tipo TEXT, mejor_version TEXT);')
    cur.execute("INSERT INTO ficheros(nombre, tipo, mejor_version) VALUES (:file, :type_file, :best_version)",
                     {'file':nombre, 'type_file': tipo, 'best_version': mejor_version})

    connection.commit()
    cur.close()

def delete_fichero_db(nombre:str, connection):
    """Borra de la tabla ficheros registros

    Args:
        nombre (str): Nombre del fichero
        connection (_type_): Conexión a la base de datos_
    """

    cur = connection.cursor()
   
    cur.execute("DELETE FROM ficheros WHERE nombre = :name", {'name':nombre})

    connection.commit()
    cur.close()


def insert_location_db(location: str, lat: float, lon:float, status:bool, connection):
    """Esta función inserta una localizacion junto a su latitud, longitud y estado en la base de datos

    Args:
        location (str): Nombre de la localización
        lat (float): Latitud geográfica de la localización
        lon (float): Longitud geográfica de la localización
        status (bool): Validez de los datos geográficos
        connection (_type_): Conexión a la base de datos
    """
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS localizaciones (descripcion TEXT, latitud REAL, longitud REAL, status INTEGER);')
    cur.execute("INSERT INTO localizaciones (descripcion, latitud, longitud, status) VALUES (:location, :lat, :lon, :status)",
                     {'location':location, 'lat': lat, 'lon': lon, 'status': status})
    
    connection.commit()
    cur.close()