import pandas as pd
from difflib import SequenceMatcher as SM
from wcag.data_api.wcag_operations import get_config_toml_wcag, get_best_wcag_compability, is_compatible_wcag_version
import pytest



def test_check_version_compatible():

    version_to_test = "2.1"

    result = is_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx', version_to_test)

    assert result is True

    version_to_test = "2.0"

    result = is_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx', version_to_test)

    assert result is True

    version_to_test = "2.2"

    result = is_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx', version_to_test)

    assert result is False


def test_check_best_version_compatible():

    version_compatible = get_best_wcag_compability('./tests/WCAG_ayuntamientos_formatted.xlsx')
    
    assert version_compatible == '2.1'


def test_wcag_adjust():

    data_wcag = pd.read_excel('./tests/WCAG_ayuntamientos_formatted.xlsx', index_col = 0)

    version = "2.1"

    config_versions_wcag= get_config_toml_wcag()


    for version_wcag in config_versions_wcag:

        if version_wcag['version'] == version:
            version_to_test = version_wcag
            
            break

    compatibility = is_compatible_wcag_version('./tests/WCAG_ayuntamientos_formatted.xlsx', version_to_test["version"])

    assert compatibility is True

    criterions_to_check = version_to_test['success_criterion']

    data_wcag_subtable = data_wcag.loc[:,["Sucess_Criterion", "Principles_Guidelines"]] 
    data_wcag_subtable = data_wcag_subtable.dropna()
    data_wcag_subtable = data_wcag_subtable["Principles_Guidelines"]
    data_wcag_subtable = data_wcag_subtable.reset_index(drop=True)

    data_wcag_criterions = data_wcag_subtable.tolist()
    
    num_criterions_losts = 0
    for criterion_to_check in criterions_to_check:
     
        found_criterion = False
        value_found = False
        # Buscamos el criterio en la tabla o alguno similar
        for value in data_wcag_criterions:

            # Tienen que pertenecer al mismo guideline
            if value[0:3] != criterion_to_check[0:3]:
                continue

            excel_criterion = value.strip()

            if criterion_to_check != excel_criterion:

                if excel_criterion in criterion_to_check:
                    data_wcag.loc[data_wcag['Principles_Guidelines'] == value, 'Principles_Guidelines'] = criterion_to_check
                    found_criterion = True
                    value_found = value
                    break
                else:
                    similitud = SM(None, criterion_to_check, value.strip()).ratio()
                    
                    if similitud >= 0.75:
                        data_wcag.loc[data_wcag['Principles_Guidelines'] == value, 'Principles_Guidelines'] = criterion_to_check
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
