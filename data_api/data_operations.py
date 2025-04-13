import urllib
import requests
import json
import sqlite3


def get_geocode(ciudad:str):
    """Llamada a la api de cartociudad para obtener datos geográficos de la ciudad

    Args:
        ciudad (str): Nombre de la ciudad a buscar

    Returns:
       python dictionary: Diccionario de python con los datos geográficos de la ciudad
    """
    ciudad = urllib.parse.quote(ciudad)
    url = f'http://www.cartociudad.es/geocoder/api/geocoder/findJsonp?q={ciudad}'
    r = requests.get(url)
    result = r.text.replace('callback(', '')[:-1]
    result = json.loads(result)

    return result or None

def get_city_data(city: str, connection):

    """Obtiene los datos de una ciudad de la base de datos

    Returns:
        list: Los datos de la base de datos para la ciudad solicitada
    """
   
    cur = connection.cursor()
    cur.execute("SELECT latitud, longitud, status FROM ciudades where ciudad = :city", {'city':city})
    result = cur.fetchall()
    cur.close()
    return result


def insert_fichero_db(nombre:str, tipo:str, mejor_version:str, connection):
    """Inserta un registro en la tabla ficheros

    Args:
        nombre (str): Nombre del fichero
        tipo (str): Tipo (si está en bruto o formateado)
        mejor_version (str): Mejor versión de wcag que cumple el fichero
        connection (_type_): Conexión a la base de datos_
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


def insert_city_db(city: str, lat: float, lon:float, status:bool, connection):
    """Esta función inserta una ciudad junto a su latitud, longitud y estado en la base de datos

    Args:
        city (str): Nombre de la ciudad
        lat (float): Latitud geográfica de la ciudad
        lon (float): Longitud geográfica de la ciudad
        status (bool): Validez de los datos geográficos
        connection (_type_): Conexión a la base de datos
    """
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ciudades (ciudad TEXT, latitud REAL, longitud REAL, status INTEGER);')
    cur.execute("INSERT INTO ciudades (ciudad, latitud, longitud, status) VALUES (:city, :lat, :lon, :status)",
                     {'city':city, 'lat': lat, 'lon': lon, 'status': status})
    
    connection.commit()
    cur.close()