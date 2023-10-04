'''Tests for importers.py
'''
import unittest


from datetime import datetime 

from pymica.io.importers import \
    import_api_smc  # pylint: disable=E0611


class TestImporters(unittest.TestCase):

    url = 'http://smcawrest01:8080/ApiRestInterna/xema/v1/mesurades/' \
          'dades/variables'
    url_meta = "http://smcawrest01:8080/ApiRestInterna/xema/v1/mesurades/metadades/estacions"

    variable = '2t'

    date = "20210401T0000Z"
    date = datetime.strptime(date, "%Y%m%dT%H%MZ")

    
    def test_import_api_smc(self):
        
        dict_out = import_api_smc(self.variable, self.url_meta,
                           self.date, self.url, None)
        
        self.assertAlmostEqual(len(dict_out), 186)
        self.assertEqual(dict_out[0]['id'],'C6')
        self.assertEqual(dict_out[0]['altitude'], 264.0) 
        
        dict_out = import_api_smc(self.variable, self.url_meta,
                           self.date, self.url, ['ZD'])
        self.assertAlmostEqual(len(dict_out), 1)
        self.assertEqual(dict_out[0]['id'],'ZD')
        self.assertEqual(dict_out[0]['altitude'], 2478.0) 
    