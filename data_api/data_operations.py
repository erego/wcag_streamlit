import urllib
import requests
import json
import sqlite3


def get_geocode(ciudad:str):
    ciudad = urllib.parse.quote(ciudad)
    url = f'http://www.cartociudad.es/geocoder/api/geocoder/findJsonp?q={ciudad}'
    r = requests.get(url)
    result = r.text.replace('callback(', '')[:-1]
    result = json.loads(result)
    #print(result)
    return result or None

def get_city_data(city, connection):

    """
    Obtiene los datos de una ciudad de la base de datos
    """
    cur = connection.cursor()
    cur.execute("SELECT latitud, longitud, status FROM ciudades where ciudad = :city", {'city':city})
    result = cur.fetchall()
    cur.close()
    return result




def create_city_db():
    """
    Esta función crea la table de ciudades en caso de no existirr
    """

    # Crear tabla de ciudades si no existiese.
    conn = sqlite3.connect('./data/database/dashboard.db')
    c = conn.cursor()
    c.execute('DROP TABLE  IF EXISTS ciudades;')
    c.execute('CREATE TABLE IF NOT EXISTS ciudades (ciudad TEXT, latitud REAL, longitud REAL, status INTEGER);')



def insert_city_db(city, lat, lon, status, connection):

    """
    Esta función inserta una ciudad junto a su latitud, longitud y estado en la base de datos
    """

    cur = connection.cursor()
    cur.execute("INSERT INTO ciudades (ciudad, latitud, longitud, status) VALUES (:city, :lat, :lon, :status)",
                     {'city':city, 'lat': lat, 'lon': lon, 'status': status})
    
    connection.commit()
    cur.close()