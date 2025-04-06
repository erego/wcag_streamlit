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