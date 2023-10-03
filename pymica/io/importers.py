"""Subroutine for reading data from SMC API 
"""

import json
import datetime
import urllib.request


from datetime import timedelta, datetime

def import_api_smc(variable: str, url_meta: str, 
                   date: datetime, url: str, station_list: list) -> list:
    """_summary_

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
        dict: dictionary containing the data ready to be interpolated.
    """

    str_variables = {'2t':'32', '2r':'33', 'ws':'30', 'wdir':'31', 'ws':'46',
                     'wdir':'47', 'ws':'48', 'wdir':'49'}

    # Mirem que la variable estigui dins les possible
    if not set(map(str, [variable])) <= set(str_variables.keys()):
            raise ValueError('Les variables disponibles són ' +
                            str(list(str_variables.keys())))

    # Mirem que station_list realment sigui una llista i ens assegurem
    if not isinstance(station_list,list):
        station_list = [None]

    json_var=urllib.request.urlopen(url_meta).read()    
    metadata=json.loads(json_var.decode("utf-8"))


    # The LOOP begins
    data = []
    # We add 5 minutes arbitrarely
    json_data = urllib.request.urlopen(
        url + "/" + str_variables[variable] + "?din=" +
        str(date.strftime("%Y-%m-%dT%H:%MZ")) + "&dfi=" +
        str(date.strftime("%Y-%m-%dT%H:%MZ"))).read()
    var_data = json.loads(json_data)

    for reg in var_data:
        if station_list == [None] or (reg['codi'] in station_list):
            for lec in reg['variables'][0]['lectures']:
                for k in range(len(metadata)):
                    if metadata[k]['codi']==reg['codi']:
                        data.append({'id': reg['codi'], 'altitude': metadata[k]['altitud'],
                                            'lat': metadata[k]['coordenades']['latitud'], 
                                            'lon': metadata[k]['coordenades']['longitud'],
                                            'value': lec['valor']})       
                                             
    return data

