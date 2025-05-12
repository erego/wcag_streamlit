from difflib import SequenceMatcher as SM

import pandas as pd
import tomllib


def get_config_toml_wcag():
    """Obtiene del fichero de configuración todo lo referente a las versiones wcag

    Returns:
        dictionary:Diccionario obtenido del fichero de configuración toml, donde para cada versión wcag se tiene los principles, guidelines y success_criterion
    """

    with open('custom.toml', 'rb') as file:
        config = tomllib.load(file)
        versions_wcag = config['wcag']
    return versions_wcag


def is_formattedfile_compatible_wcag_version(path_to_file:str, wcag_version:str)->bool : 
    """Función que comprueba si determinada versión de wcag es compatible con un fichero. Devuelve falso si no lo es

    Args:
        path_to_file (str): Ruta al fichero a comprobar
        wcag_version (str): Versión de wcag
    Returns:
        bool: Devuelve True si lo es y False en caso contrario
    """

    config_versions_wcag= get_config_toml_wcag()


    for version_wcag in config_versions_wcag:

        if version_wcag['version'] == wcag_version:
            version_config_to_test = version_wcag
            
            break

    data_wcag = pd.read_excel(path_to_file, index_col = 0)
    data_wcag_subtable = data_wcag.loc[:,["Sucess_Criterion", "Principles_Guidelines"]] 
    data_wcag_subtable = data_wcag_subtable.dropna()
    data_wcag_subtable = data_wcag_subtable["Principles_Guidelines"]
    data_wcag_subtable = data_wcag_subtable.reset_index(drop=True)
    data_wcag_criterions = data_wcag_subtable.tolist()
    
    is_compatible = True
    # Recorremos los criterios segun la configuración de esa versión a comprobar
    criterions_to_check = version_config_to_test['success_criterion']

    leves_in_dataframe = get_levels_criterion_from_dataframe(data_wcag)

    for criterion_to_check in criterions_to_check:

        level_to_check = get_level_from_criterion(wcag_version, config_versions_wcag, criterion_to_check)
        if level_to_check not in leves_in_dataframe:
            continue

        criterion_to_check=criterion_to_check.replace(":", "")
        found_criterion = False

        # Buscamos el criterio en la tabla o alguno similar
        for value in data_wcag_criterions:

            # Tienen que pertenecer al mismo criterio
            excel_criterion = value.strip().replace(":", "")
    
            if excel_criterion.split()[0] != criterion_to_check.split()[0]:
                continue

            if criterion_to_check != excel_criterion:
                
                if excel_criterion not in criterion_to_check:

                    similitud = SM(None, criterion_to_check, value.strip()).ratio()
                    
                    if similitud >= 0.70:
                        found_criterion = True  
                        break

                else:
                    found_criterion = True
                    break

            else:
                found_criterion = True
                break

        if not found_criterion:
            is_compatible = False 
            break     

    return is_compatible


def is_rawfile_compatible_wcag_version(data_wcag:pd.DataFrame, wcag_version:str)->bool : 
    """Función que comprueba si determinada versión de wcag es compatible con un pandas dataframe. Devuelve falso si no lo es

    Args:
        data_wcag (pandas DataFrame): DataFrame de pandas
        wcag_version (str): Versión de wcag
    Returns:
        bool: Devuelve True si lo es y False en caso contrario
    """

    config_versions_wcag= get_config_toml_wcag()


    for version_wcag in config_versions_wcag:

        if version_wcag['version'] == wcag_version:
            version_config_to_test = version_wcag
            
            break

    data_wcag_subtable = data_wcag.loc[:,["Sucess_Criterion", "Principles_Guidelines"]] 
    data_wcag_subtable = data_wcag_subtable.dropna()
    data_wcag_subtable = data_wcag_subtable["Principles_Guidelines"]
    data_wcag_subtable = data_wcag_subtable.reset_index(drop=True)
    data_wcag_criterions = data_wcag_subtable.tolist()
    
    is_compatible = True

    # Recorremos los criterios segun la configuración de esa versión a comprobar
    criterions_to_check = version_config_to_test['success_criterion']

    leves_in_dataframe = get_levels_criterion_from_dataframe(data_wcag)

    for criterion_to_check in criterions_to_check:
            
        level_to_check = get_level_from_criterion(wcag_version, config_versions_wcag, criterion_to_check)
        if level_to_check not in leves_in_dataframe:
            continue

        criterion_to_check=criterion_to_check.replace(":", "")
        found_criterion = False

        # Buscamos el criterio en la tabla o alguno similar
        for value in data_wcag_criterions:

            # Tienen que pertenecer al mismo criterio
            excel_criterion = value.strip().replace(":", "")
    
            if excel_criterion.split()[0] != criterion_to_check.split()[0]:
                continue

            if criterion_to_check != excel_criterion:

                if excel_criterion not in criterion_to_check:

                    similitud = SM(None, criterion_to_check, value.strip()).ratio()
                    
                    if similitud >= 0.70:
                        found_criterion = True  
                        break
                else:
                    found_criterion = True
                    break

            else:
                found_criterion = True
                break

        if not found_criterion:
            is_compatible = False 
            break     

    return is_compatible

def get_best_wcag_compability_formattedfile(path_to_file:str)-> str:
    """Función que devuelve la mejor compatibilidad de un fichero con una versión de wcag

    Args:
        path_to_file (str): Ruta al fichero con los datos

    Returns:
        str: Devuelve la mejor version para la que es compatible
    """
 
    config_versions_wcag= get_config_toml_wcag()

    for config_version_wcag in reversed(config_versions_wcag):

        version_to_check = config_version_wcag["version"]

        if is_formattedfile_compatible_wcag_version(path_to_file, version_to_check):
            return version_to_check
 
    return None

def get_best_wcag_compability_rawfile(data_wcag:pd.DataFrame)-> str:
    """Función que devuelve la mejor compatibilidad de un dataframe de pandas con una versión de wcag

    Args:
        data_wcag (pandas DataFrame): DataFRame de pandas a comprobar

    Returns:
        str: Devuelve la mejor version para la que es compatible
    """
 
    config_versions_wcag= get_config_toml_wcag()

    for config_version_wcag in reversed(config_versions_wcag):

        version_to_check = config_version_wcag["version"]

        if is_rawfile_compatible_wcag_version(data_wcag, version_to_check):
            return version_to_check
 
    return None


def get_wcag_data_filtered(wcag_data: pd.DataFrame, version_to_filter: str):
    """Función que filtra un pandas DataFrame teniendo en cuenta la versión a la que queremos ajustarlo

    Args:
        wcag_data (pd.DataFrame): pandas DataFrame a filtrar
        version_to_filter (str): Versión que queremos usar de referencia para filtrar
    """

def get_principles(version_wcag:str, configs_wcag):

    """Dada una versión de wcag, busca en el conjunto de wcag del fichero
    de configuración, los principios asociados a dicha versión

        Args:
        version_wcag (str): Versión wcag elegida
        configs_wcag (dictionary): Diccionario de configuración de versiones wcag

    Returns:
        list: List con los principios de esa versión wcag
    """
    filtered_principles = [config_wcag['principles'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return filtered_principles

def get_guidelines(version_wcag:str, configs_wcag):

    """Dada una versión de wcag, busca en el conjunto de wcag del fichero
    de configuración, las pautas principales asociadzs a dicha versión

        Args:
        version_wcag (str): Versión wcag elegida
        configs_wcag (dictionary): Diccionario de configuración de versiones wcag

    Returns:
        list: List con las pautas principales de esa versión wcag
    """
    filtered_guidelines = [config_wcag['guidelines'] for config_wcag in configs_wcag 
                           if config_wcag['version'] ==  version_wcag][0]
    return filtered_guidelines


def get_success_criterion(version_wcag:str, configs_wcag):

    """Obtiene los criterios de éxito asociados a una versión de wcag

        Args:
        version_wcag (str): Versión wcag elegida
        configs_wcag (dictionary): Diccionario de configuración de versiones wcag

    Returns:
        list: List con los criterios de éxito de esa versión wcag
    """

    success_criterion = [config_wcag['success_criterion'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return success_criterion

def get_levels_criterion(version_wcag:str, configs_wcag):

    """Obtiene los criterios de éxito y sus niveles asociados a una versión de wcag

        Args:
        version_wcag (str): Versión wcag elegida
        configs_wcag (dictionary): Diccionario de configuración de versiones wcag

    Returns:
        list: List con los niveles y sus criterios para esa versión wcag
    """

    levels = [config_wcag['levels'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return levels



def get_levels_criterion_from_dataframe(dataframe_levels:pd.DataFrame):


    """Obtiene los niveles asociados a un dataframe que puede estar filtrado

        Args:
        dataframe_levels (pd.DataFrame): Dataframe del que extraer los niveles

    Returns:
        list: List con los niveles 
    """

    levels_column = list(set(dataframe_levels['Sucess_Criterion'].dropna()))
    levels_column.sort()
    return levels_column


def get_level_from_criterion(version_wcag:str, configs_wcag, criterion:str):
    """Obtiene el nivel asociado a un criterio de una versión de wcag

        Args:
        version_wcag (str): Versión wcag elegida
        configs_wcag (dictionary): Diccionario de configuración de versiones wcag
        criterion (str): Criterio del que obtener el nivel
    Returns:
        str: Level de dicho criterio
    """
    levels_criterion = get_levels_criterion(version_wcag, configs_wcag)
    for level_criterion in levels_criterion:
        if level_criterion["criterion"] == criterion:
            return level_criterion["level"]
