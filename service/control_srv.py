import logging
import requests
import pandas as pd

from config.config import CONFIG_APP

class GeoAPI(object):

    API_KEY = CONFIG_APP["app"]["apigeo"]
    LAT = CONFIG_APP["app"]["lat"]
    LON = CONFIG_APP["app"]["lon"]
        
    def __init__(self):
        super()
        
    @classmethod
    def is_hot_in_pehuajo(cls):
        try:
            query = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(cls.LAT,
            cls.LON,
            cls.API_KEY)
            resp = requests.post(query)
            datos = resp.json()
            temp = datos["main"]["temp"]
            logging.debug(temp)
            if (temp > 28):
                return True
            return False
        except Exception as e:
            logging.debug(e)
            return False
        
class ControlStock(object):

    def __init__(self):
        super()
        self.productos = None
        self.initLoad()
    
    def initLoad(self):
        self.productos = pd.DataFrame({"product_name": ["Chocolate",
            "Granizado", "Limon", "Dulce de Leche"], "quantity":
            [3,10,0,5]})
        self.productos.head()

    def is_product_available(self,product_name, quantity):
        try:
            filter1=self.productos.loc[self.productos['product_name'] == product_name]
            if len(filter1)>0:
                filter2 = self.productos.loc[(self.productos['product_name'] == product_name) & 
                (self.productos['quantity'] >= quantity)]
                if len(filter2) >0:
                    return True
            return False
        except KeyError as e:
            logging.debug(e)
            return False
        except Exception as e:
            logging.debug(e)
            return False

class ControlCode(object):
    
    _AVAILABLE_DISCOUNT_CODES = ["Primavera2021", "Verano2021","Navidad2x1", "heladoFrozen"]

    def __init__(self):
        super()
    
    def include_character(self,character,check_str):
        return (character in check_str)

    def count_differents(self,orig_str,dest_str):
        cant_orig = 0
        for item in orig_str:
            if not self.include_character(item,dest_str):
                cant_orig=cant_orig +1
        return cant_orig

    def validate_discount_code(self,discount_code):
        valid = False
        for item in self._AVAILABLE_DISCOUNT_CODES:
            cant_orig = self.count_differents(discount_code,item)
            cant_dest = self.count_differents(item,discount_code)
            logging.debug("Cantidad orig: {}".format(cant_orig))
            logging.debug("Cantidad dest: {}".format(cant_dest))
            if (item.lower() == discount_code.lower()):
                if ((cant_orig + cant_dest) <3):
                    valid = True
                    break

        return valid
