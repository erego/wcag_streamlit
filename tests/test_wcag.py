from difflib import SequenceMatcher as SM
import pandas as pd
from ..data_api.wcag_operations import get_config_toml_wcag, get_best_wcag_compability_formattedfile
from ..data_api.wcag_operations import is_formattedfile_compatible_wcag_version, is_rawfile_compatible_wcag_version
from ..data_api.wcag_operations import get_levels_criterion, get_levels_criterion_from_dataframe
from ..data_api.wcag_operations import get_level_from_criterion

def test_check_version_compatible_formattedfile():
    """Comprueba si un fichero es compatible con diferentes versiones
    """

    version_to_test = "2.1"

    result = is_formattedfile_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx',
                                                      version_to_test)
    assert result is True
    version_to_test = "2.0"
    result = is_formattedfile_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx',
                                                      version_to_test)
    assert result is True
    version_to_test = "2.2"
    result = is_formattedfile_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx',
                                                      version_to_test)
    assert result is False

def test_get_level_from_criterion():
    """Comprueba el nivel de un criterio
    """
    version_to_test = "2.1"
    criterion_to_test= "1.2.6 Sign Language (Prerecorded)"
    configs_wcag = get_config_toml_wcag()
    result = get_level_from_criterion(version_to_test, configs_wcag, criterion_to_test)
    assert result == "AAA"

def test_get_levels():
    """Comprueba los niveles que puede tener una versión de wcag
    """
    version_to_test = "2.1"
    configs_wcag = get_config_toml_wcag()
    levels_criterion = get_levels_criterion(version_to_test, configs_wcag)
    list_of_levels = {element["level"] for element in levels_criterion}   
    assert len(list_of_levels) == 3
    assert 'AAA' in list_of_levels

def test_get_levels_dataframe():
    data_wcag_subtable = pd.read_excel('./tests/WCAG_ayuntamientos_formatted.xlsx', index_col = 0)
    levels_criterion = get_levels_criterion_from_dataframe(data_wcag_subtable)
    assert len(levels_criterion) == 3
    assert 'AAA' in levels_criterion
  
def test_check_version_compatible_rawfile():
    """Comprueba si un fichero es compatible con distintas versiones de wcag
    """

    data_wcag = pd.read_excel('./tests/Datos WCAG Ayuntamientos.xlsx')

    num_columns = data_wcag.shape[1]
    # Borramos las dos últimas columnas pues son iguales a las dos primeras
    data_wcag.drop(columns=[data_wcag.columns[num_columns-1],
                            data_wcag.columns[num_columns-2]], inplace = True)
    # Eliminamos las filas que son todo NA(filas en blanco)
    data_wcag.dropna(how='all', inplace=True)
    data_wcag.reset_index(drop=True, inplace=True)

    # Renombramos las primeras dos columnas vacías por otros nombres más significativos
    data_wcag.rename(columns = {data_wcag.columns[0]: 'Sucess_Criterion', data_wcag.columns[1]: 'Principles_Guidelines'}, inplace=True)

    version_to_test = "2.1"

    result = is_rawfile_compatible_wcag_version(data_wcag, version_to_test)
  
    assert result is True

    version_to_test = "2.0"

    result = is_rawfile_compatible_wcag_version(data_wcag, version_to_test)

    assert result is True

    version_to_test = "2.2"

    result = is_rawfile_compatible_wcag_version(data_wcag, version_to_test)

    assert result is False

def test_check_version_compatible_rawfile_museo():

    """Comprueba si el fichero de museos es compatible con diferentes versiones
    """

    data_wcag = pd.read_excel('./tests/Datos WCAG Museos.xlsx')

    num_columns = data_wcag.shape[1]
    # Borramos las dos últimas columnas pues son iguales a las dos primeras
    data_wcag.drop(columns=[data_wcag.columns[num_columns-1],
                            data_wcag.columns[num_columns-2]], inplace = True)
    # Eliminamos las filas que son todo NA(filas en blanco)
    data_wcag.dropna(how='all', inplace=True)
    data_wcag.reset_index(drop=True, inplace=True)

    # Renombramos las primeras dos columnas vacías por otros nombres más significativos
    data_wcag.rename(columns = {data_wcag.columns[0]: 'Sucess_Criterion', data_wcag.columns[1]: 'Principles_Guidelines'}, inplace=True)

    version_to_test = "2.1"

    result = is_rawfile_compatible_wcag_version(data_wcag, version_to_test)
    assert result is True

def test_check_best_version_compatible_formattedfile():
    """Comprueba cuál es la mejor versión de wcag para un fichero
    """

    version_compatible = get_best_wcag_compability_formattedfile('./tests/WCAG_ayuntamientos_formatted.xlsx')
    assert version_compatible == '2.1'

def test_wcag_adjust_formattedfile():

    data_wcag = pd.read_excel('./tests/WCAG_ayuntamientos_formatted.xlsx', index_col = 0)

    version = "2.1"

    config_versions_wcag= get_config_toml_wcag()


    for version_wcag in config_versions_wcag:

        if version_wcag['version'] == version:
            version_to_test = version_wcag
            
            break

    compatibility = is_formattedfile_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx',
                                                              version_to_test["version"])

    assert compatibility is True

    criterions_to_check = version_to_test['success_criterion']
    data_wcag_subtable = data_wcag.loc[:,["Sucess_Criterion", "Principles_Guidelines"]]
    data_wcag_subtable = data_wcag_subtable.dropna()
    data_wcag_subtable = data_wcag_subtable["Principles_Guidelines"]
    data_wcag_subtable = data_wcag_subtable.reset_index(drop=True)
    data_wcag_criterions = data_wcag_subtable.tolist()
    num_criterions_losts = 0
    for criterion_to_check in criterions_to_check:
        criterion_to_check=criterion_to_check.replace(":", "")
        found_criterion = False
        value_found = False
        
        # Buscamos el criterio en la tabla o alguno similar
        for value in data_wcag_criterions:

            # Tienen que pertenecer al mismo criterio
            excel_criterion = value.strip().replace(":", "")
            if excel_criterion.split()[0] != criterion_to_check.split()[0]:
                continue

            if criterion_to_check != excel_criterion:

                if excel_criterion in criterion_to_check:
                    data_wcag.loc[data_wcag['Principles_Guidelines'] == value, 'Principles_Guidelines'] = criterion_to_check
                    found_criterion = True
                    value_found = value
                    break
                else:
                    similitud = SM(None, criterion_to_check, value.strip()).ratio()
                    if similitud >= 0.70:
                        data_wcag.loc[data_wcag['Principles_Guidelines'] == value,
                                      'Principles_Guidelines'] = criterion_to_check
                        found_criterion = True
                        value_found = value
                        break
            else:
                found_criterion = True
                value_found = value

        if found_criterion is False:
            num_criterions_losts+=1
        else:
            data_wcag_criterions.remove(value_found)

    assert num_criterions_losts == 0
    assert len(data_wcag_criterions) == 0
    data_wcag.to_excel('./tests/WCAG_ayuntamientos_formatted_check.xlsx')
