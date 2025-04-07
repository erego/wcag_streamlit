import pandas as pd
from difflib import SequenceMatcher as SM
from wcag.data_api.wcag_operations import get_config_toml_wcag, get_best_wcag_compability


def test_check_version_compatible():

    version_compatible = get_best_wcag_compability('./tests/WCAG_ayuntamientos_formatted.xlsx')
    
    assert version_compatible == '2.2'


def test_wcag_adjust():

    data_wcag = pd.read_excel('./tests/WCAG_ayuntamientos_formatted.xlsx', index_col = 0)

    version = "2.1"

    config_versions_wcag= get_config_toml_wcag()


    for version_wcag in config_versions_wcag:

        if version_wcag['version'] == version:
            version_to_test = version_wcag
            
            break

    assert version_to_test is not None

    criterions_to_check = version_to_test['success_criterion']

    found_criterions = True

    data_wcag_subtable = data_wcag.loc[:,["Sucess_Criterion", "Principles_Guidelines"]] 
    data_wcag_subtable = data_wcag_subtable.dropna()
    data_wcag_subtable = data_wcag_subtable["Principles_Guidelines"]
    data_wcag_subtable = data_wcag_subtable.reset_index(drop=True)

    num_criterions_table = data_wcag_subtable.shape[0]
    num_criterions_config = len(criterions_to_check)

    assert num_criterions_table == num_criterions_config

    num_error = 0

    for index, value in data_wcag_subtable.items():
        # Get element index from list of criterion
        criterion_to_check = criterions_to_check[index].strip()
        excel_criterion = value.strip()

        if criterion_to_check != excel_criterion:

            if excel_criterion in criterion_to_check:
                data_wcag.loc[data_wcag['Principles_Guidelines'] == value, 'Principles_Guidelines'] = criterion_to_check

            else:
                similitud = SM(None, criterion_to_check, value.strip()).ratio()
                
                if similitud < 0.75:
                    found_criterions = False         
                    error+= 1
                else:
                    data_wcag.loc[data_wcag['Principles_Guidelines'] == value, 'Principles_Guidelines'] = criterion_to_check

  
    assert num_error == 0
    assert found_criterions is True

