import sqlite3
import pytest

from wcag.data_api.data_operations import get_geocode, get_city_data


def test_city_database_wrong():

    """
    Comprueba la inserción en la tabla ciudades
    """

    # Crear tabla de ciudades si no existiese.
    conn = sqlite3.connect('./tests/dashboard_test.db')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS ciudades')
    cur.execute('CREATE TABLE IF NOT EXISTS ciudades (ciudad TEXT, latitud REAL, longitud REAL, status INTEGER);')

    city="Oursense"

    result = get_city_data(city, conn)

 
    if len(result) == 0:
        data_to_insert = get_geocode(city)
        status =  True
        if data_to_insert is None:
            lat = 0.0
            lon = 0.0
            status =  False
        else:
            lat = data_to_insert["lat"]
            lon = data_to_insert["lng"]
           

        assert status is False


        cur.execute("INSERT INTO ciudades (ciudad, latitud, longitud, status) VALUES (:city, :lat, :lon, :status)",
                     {'city':city, 'lat': lat, 'lon': lon, 'status': status})

        assert cur.rowcount == 1

        conn.commit()

        

    cur.close()    


def test_city_database():

    """
    Comprueba la inserción en la tabla ciudades
    """

    # Crear tabla de ciudades si no existiese.
    conn = sqlite3.connect('./tests/dashboard_test.db')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS ciudades')
    cur.execute('CREATE TABLE IF NOT EXISTS ciudades (ciudad TEXT, latitud REAL, longitud REAL, status INTEGER);')

    city="Cádiz"
    result = get_city_data(city, conn)

 
    if len(result) == 0:
        data_to_insert = get_geocode(city)
        status =  True
        if data_to_insert is None:
            lat = 0.0
            lon = 0.0
            status =  False
        else:
            lat = data_to_insert["lat"]
            lon = data_to_insert["lng"]
           

        assert status is True

        cur.execute("INSERT INTO ciudades (ciudad, latitud, longitud, status) VALUES (:city, :lat, :lon, :status)",
                     {'city':city, 'lat': lat, 'lon': lon, 'status': status})

        
        assert cur.rowcount == 1
   
        conn.commit()

    result = get_city_data(city, conn)

    lat = result[0][0]
    lon = result[0][1]
    status = result[0][2]

    assert lat == pytest.approx(36.51787871)
    assert lon == pytest.approx(-6.280467)
    assert status == 1

    cur.close()    
         





      