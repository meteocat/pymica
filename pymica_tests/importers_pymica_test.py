'''Tests for importers.py
'''
import unittest


import dateutil.parser

from pymica.io.importers import \
    import_api_smc  # pylint: disable=E0611


class TestImporters(unittest.TestCase):

    url = 'http://smcawrest01:8080/ApiRestInterna/xema/v1/mesurades/' \
          'dades/variables'
    url_meta = "http://smcawrest01:8080/ApiRestInterna/xema/v1/mesurades/metadades/estacions"

    station_list = ["C6","C7","C8","CE","CW","D1","D7","D8","D9","DI","DK","DQ","H1","MR","U3","UH","UJ","UM","V1","V8",
                "VA","VB","VC","VD","VM","VY","VQ","W4","W8","WB","WC","WD","WJ","WL","WP","WV","WZ","XA","XB","XD",
                "X1","XE","XI","XM","XP","XR","XX","Y6","YD","YJ","YF","YH","YE","YL","YO"]
    
    #station_list = ["ZD"]
    station_list = None
    
    variable = '2t'

    date = "20210401T0000Z"
    date = dateutil.parser.parse(date)

    
    def test_import_api_smc(self):
        
        dict_out = import_api_smc(self.variable, self.url_meta,
                           self.date, self.url, self.station_list)
        
        if self.station_list == None:
            self.assertAlmostEqual(len(dict_out), 186)
            self.assertEqual(dict_out[0]['id'],'C6')
            self.assertEqual(dict_out[0]['altitude'], 264.0) 
        else:
            self.assertAlmostEqual(len(dict_out), 1)
            self.assertEqual(dict_out[0]['id'],'ZD')
            self.assertEqual(dict_out[0]['altitude'], 2478.0) 
        