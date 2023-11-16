# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 13:32:38 2023

@author: user
"""

from zeep import Client

client = Client('http://192.168.141.59:8000/?wsdl')
result1 = client.service.temps(90 , 80, 80, 1 )

print (result1)