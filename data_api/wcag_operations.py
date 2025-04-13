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


def is_compatible_wcag_version(path_to_file:str, wcag_version:str)->bool : 
    """Función que comprueba si determinada versión de wcag es compatible con un fichero. Devuelve falso si no lo es

    Args:
        path_to_file (str): _description_
        wcag_version (str): _description_
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

    for criterion_to_check in criterions_to_check:

        found_criterion = False

        # Buscamos el criterio en la tabla o alguno similar
        for value in data_wcag_criterions:

            # Tienen que pertenecer al mismo guideline
            if value[0:3] != criterion_to_check[0:3]:
                continue


            excel_criterion = value.strip()

            if criterion_to_check != excel_criterion:

                if excel_criterion not in criterion_to_check:

                    similitud = SM(None, criterion_to_check, value.strip()).ratio()
                    
                    if similitud >= 0.75:
                        found_criterion = True  
                        break
                else:
                    found_criterion = True
                    break

            else:
                found_criterion = True
                break

        if found_criterion == False:
            is_compatible = False 
            break     

    return is_compatible

def get_best_wcag_compability(path_to_file:str)-> str:
    """Función que devuelve la mejor compatibilidad de un fichero con una versión de wcag

    Args:
        path_to_file (str): Ruta al fichero con los datos

    Returns:
        str: Devuelve la mejor version para la que es compatible
    """
 
    config_versions_wcag= get_config_toml_wcag()

    for config_version_wcag in reversed(config_versions_wcag):

        version_to_check = config_version_wcag["version"]

        if is_compatible_wcag_version(path_to_file, version_to_check):
            return version_to_check
 
    return None


def get_wcag_compability(path_to_file:str, version_to_compare:dict)-> bool:
    """Función que valida la compatibilidad de un fichero con una versión de wcag

    Args:
        path_to_file (str): Ruta al fichero con los datos
        version_to_compare (dict): Configuración de la versión de wcag del fichero de configuración TOML

    Returns:
        bool: Devuelve verdadero si es compatible, en caso contrario devuelve falso
    """

    is_compatible = False

    data_wcag = pd.read_excel(path_to_file, index_col = 0)
    data_wcag_subtable = data_wcag.loc[:,["Sucess_Criterion", "Principles_Guidelines"]] 
    data_wcag_subtable = data_wcag_subtable.dropna()
    data_wcag_subtable = data_wcag_subtable["Principles_Guidelines"]
    data_wcag_subtable = data_wcag_subtable.reset_index(drop=True)
    num_criterions_table = data_wcag_subtable.shape[0]

    criterions_to_check = version_to_compare['success_criterion']
    num_criterions_config = len(criterions_to_check)
    
    found_compatible_criterions = True

    if num_criterions_table == num_criterions_config:
        for index, value in data_wcag_subtable.items():
            # Get element index from list of criterion
            criterion_to_check = criterions_to_check[index].strip()
            excel_criterion = value.strip()

            if criterion_to_check != excel_criterion:

                if excel_criterion not in criterion_to_check:
                    similitud = SM(None, criterion_to_check, value.strip()).ratio()
                    
                    if similitud < 0.75:
                        found_compatible_criterions = False         
    
        if found_compatible_criterions is True:
            is_compatible = True

    return is_compatible


def get_principles(version_wcag:str, configs_wcag):

    """_summary_

        Args:
        version_wcag (str): Versión wcag elegida
        configs_wcag (dictionary): Diccionario de configuración de versiones wcag

    Returns:
        list: List con los principios de esa versión wcag
    """

    filtered_principles = [config_wcag['principles'] for config_wcag in configs_wcag if config_wcag['version'] ==  version_wcag][0]
    return filtered_principles