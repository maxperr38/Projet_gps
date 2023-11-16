# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 10:01:17 2023

@author: user
"""

import openrouteservice as ors
import folium

client = ors.Client(key='214b4197499b29ec9ba86ef1100ca6c0')

import operator
from functools import reduce

m = folium.Map(location=list(reversed([-77.0362619, 38.897475])), tiles="cartodbpositron", zoom_start=13)

# white house to the pentagon
coords = [[-77.0362619, 38.897475], [-77.0584556, 38.871861]]

route = client.directions(coordinates=coords,
                          profile='foot-walking',
                          format='geojson')

waypoints = list(dict.fromkeys(reduce(operator.concat, list(map(lambda step: step['way_points'], route['features'][0]['properties']['segments'][0]['steps'])))))

folium.PolyLine(locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']], color="blue").add_to(m)

folium.PolyLine(locations=[list(reversed(route['features'][0]['geometry']['coordinates'][index])) for index in waypoints], color="red").add_to(m)

m