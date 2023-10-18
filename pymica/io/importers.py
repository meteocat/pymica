"""Module to import data from different sources and transform it to pymica format.
"""

import json
import urllib.request
from datetime import datetime


def import_api_smc(
    variable: str, url_meta: str, date: datetime, url: str, station_list: list
) -> list:
    """

    Args:
        variables (str): String containing the name of the variables.
        url_meta (str): String which contains the url for download the metadata
        date (datetime): Is the time for which we obtained the data
        url (str): String which contains the url for download the metadata
        station_list (list): List with the codes of stations to be extracted.
                             If its None returns all the available stations.

    Raises:
        ValueError: Check if the variables are available.

    Returns:
        dict: Dictionary containing the data ready to be interpolated.
    """

    str_variables = {
        "2t": "32",
        "2r": "33",
        "ws_2": "30",
        "wdir_2": "31",
        "ws_6": "46",
        "wdir_6": "47",
        "ws_10": "48",
        "wdir_10": "49",
    }

    # Check if the varible is among the available ones
    if not set(map(str, [variable])) <= set(str_variables.keys()):
        raise ValueError(
            "Les variables disponibles són " + str(list(str_variables.keys()))
        )

    # Check if station_list is a list, otherwise, [None] to consider them all
    if not isinstance(station_list, list):
        station_list = [None]

    json_var = urllib.request.urlopen(url_meta).read()
    metadata = json.loads(json_var.decode("utf-8"))

    data = []

    json_data = urllib.request.urlopen(
        url
        + "/"
        + str_variables[variable]
        + "?din="
        + str(date.strftime("%Y-%m-%dT%H:%MZ"))
        + "&dfi="
        + str(date.strftime("%Y-%m-%dT%H:%MZ"))
    ).read()
    var_data = json.loads(json_data)

    for reg in var_data:
        if station_list == [None] or (reg["codi"] in station_list):
            for lec in reg["variables"][0]["lectures"]:
                for k in range(len(metadata)):
                    if metadata[k]["codi"] == reg["codi"]:
                        data.append(
                            {
                                "id": reg["codi"],
                                "altitude": metadata[k]["altitud"],
                                "lat": metadata[k]["coordenades"]["latitud"],
                                "lon": metadata[k]["coordenades"]["longitud"],
                                "value": lec["valor"],
                            }
                        )

    return data
