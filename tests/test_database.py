"""Página para los tests relacionados con la base de datos
"""

import sqlite3
import pytest

import streamlit as st

from ..data_api.data_operations import get_geocode, get_location_data
from ..data_api.wcag_operations import get_best_wcag_compability_formattedfile

def test_file_database():
    """Comprueba la inserción de las características de un fichero en la base de datos
    """

    # Crear tabla de fichero si no existiese.
    conn = sqlite3.connect(st.secrets.db_test.path)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS ficheros')
    cur.execute('CREATE TABLE IF NOT EXISTS ficheros (nombre TEXT, tipo TEXT, mejor_version TEXT);')

    file = "Datos WCAG Ayuntamientos.xlsx"
    type_file = "raw"

    best_version =  get_best_wcag_compability_formattedfile(
        './tests/WCAG_ayuntamientos_formatted.xlsx')

    cur.execute("INSERT INTO ficheros(nombre, tipo, mejor_version) " \
    "VALUES (:file, :type_file, :best_version)",
                     {'file':file, 'type_file': type_file, 'best_version': best_version})
    assert cur.rowcount == 1

    conn.commit()
    cur.close()

def test_location_database_wrong():

    """
    Comprueba la inserción en la tabla localizaciones
    """

    # Crear tabla de localizaciones si no existiese.
    conn = sqlite3.connect(st.secrets.db_test.path)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS localizaciones')
    cur.execute('CREATE TABLE IF NOT EXISTS localizaciones (descripcion TEXT, latitud REAL, ' \
    'longitud REAL, status INTEGER);')

    location="Oursense"

    result = get_location_data(location, conn)

    if len(result) == 0:
        data_to_insert = get_geocode(location)
        status =  True
        if data_to_insert is None:
            lat = 0.0
            lon = 0.0
            status =  False
        else:
            lat = data_to_insert["lat"]
            lon = data_to_insert["lng"]
        
        assert status is False

        cur.execute("INSERT INTO localizaciones (descripcion, latitud, longitud, status) " \
        "VALUES (:location, :lat, :lon, :status)",
                     {'location':location, 'lat': lat, 'lon': lon, 'status': status})

        assert cur.rowcount == 1

        conn.commit()

    cur.close()

def test_location():
    """Comprueba la función de obtener el geocode de un lugar
    """
    location="Museo de la Ciencia de Valladolid"
    data_return = get_geocode(location)
    data_to_test = data_return["address"]
    assert data_to_test=='MUSEO DE LA CIENCIA DE VALLADOLID'

def test_location_modify_database():

    """
    Comprueba la modificación en la tabla localizaciones
    """

    # Crear tabla de localizaciones si no existiese.
    conn = sqlite3.connect(st.secrets.db_test.path)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS localizaciones')
    cur.execute('CREATE TABLE IF NOT EXISTS localizaciones (descripcion TEXT, latitud REAL, longitud REAL, status INTEGER);')

    location_old="Oursense"
    result = get_location_data(location_old, conn)
    if len(result) == 0:
        data_to_insert = get_geocode(location_old)
        status =  True
        if data_to_insert is None:
            lat = 0.0
            lon = 0.0
            status =  False
        else:
            lat = data_to_insert["lat"]
            lon = data_to_insert["lng"]

        cur.execute("INSERT INTO localizaciones (descripcion, latitud, longitud, status) VALUES (:location, :lat, :lon, :status)",
                     {'location':location_old, 'lat': lat, 'lon': lon, 'status': status})

        assert cur.rowcount == 1
        conn.commit()

    location="Ourense"
    result = get_location_data(location, conn)
    data_to_insert = get_geocode(location)
    status =  True
    if data_to_insert is None:
        lat = 0.0
        lon = 0.0
        status =  False
    else:
        lat = data_to_insert["lat"]
        lon = data_to_insert["lng"]

    assert status is True

    cur.execute("UPDATE localizaciones SET descripcion = :location, latitud = :lat, longitud = :lon, status = :status WHERE descripcion = :old_description",
                     {'location':location, 'lat': lat, 'lon': lon, 'old_description': location_old, 'status': status})

    conn.commit()

    result = get_location_data(location, conn)

    lat = result[0][0]
    lon = result[0][1]
    status = result[0][2]

    assert lat == pytest.approx(42.3385705)
    assert lon == pytest.approx(-7.86427465)
    assert status == 1

    cur.close()

def test_location_database():

    """
    Comprueba la inserción en la tabla localizaciones
    """

    # Crear tabla de localizaciones si no existiese.
    conn = sqlite3.connect(st.secrets.db_test.path)
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS localizaciones')
    cur.execute('CREATE TABLE IF NOT EXISTS localizaciones (descripcion TEXT, latitud REAL, longitud REAL, status INTEGER);')

    location="Cádiz"
    result = get_location_data(location, conn)
    if len(result) == 0:
        data_to_insert = get_geocode(location)
        status =  True
        if data_to_insert is None:
            lat = 0.0
            lon = 0.0
            status =  False
        else:
            lat = data_to_insert["lat"]
            lon = data_to_insert["lng"]
        assert status is True

        cur.execute("INSERT INTO localizaciones (descripcion, latitud, longitud, status) VALUES (:location, :lat, :lon, :status)",
                     {'location':location, 'lat': lat, 'lon': lon, 'status': status})

        assert cur.rowcount == 1
        conn.commit()

    result = get_location_data(location, conn)

    lat = result[0][0]
    lon = result[0][1]
    status = result[0][2]

    assert lat == pytest.approx(36.51787871)
    assert lon == pytest.approx(-6.280467)
    assert status == 1

    cur.close()
