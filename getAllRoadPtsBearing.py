

from shapely.geometry import LineString, Point
import geopy.distance

import requests
import numpy as np
import time
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
import math

start_time = time.time()

import pandas as pd

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
way
  (14.717189,101.615757,14.897189,101.795757);
out geom;
"""
#20 * 20 km

def computeBearing(fro, to):
    y = math.sin(to[1]-fro[1]) * math.cos(to[0])
    x = math.cos(fro[0])*math.sin(to[0]) - math.sin(fro[0])*math.cos(to[0])*math.cos(to[1]-fro[1])
    θ = math.atan2(y, x)
    brng = (θ*180/math.pi + 360) % 360
    return brng

def computePointOnField(fro, theta, d):
    R = 6371e3
    Ad = d/R
    theta = math.radians(theta)
    la1 = math.radians(fro[0])
    lo1 = math.radians(fro[1])
    la2 =  math.asin(math.sin(la1) * math.cos(Ad) + math.cos(la1) * math.sin(Ad) * math.cos(theta))
    lo2 = lo1 + math.atan2(math.sin(theta) * math.sin(Ad) * math.cos(la1) , math.cos(Ad) - math.sin(la1) * math.sin(la2))
    return (math.degrees(la2),math.degrees(lo2))

response = requests.get(overpass_url,
                        params={'data': overpass_query})
data = response.json()
roadPoints = []
fieldPoints1 = []
fieldPoints2 = []
originalPoints = []
j = 0
i = 0
smallest = 0.01
ps = []
for element in data['elements']:
    if element['type'] == 'way':
        print('Points ', ps)

        geo = element['geometry']
        way = []
        for p in geo:
            way.append((p['lat'], p['lon']))

            originalPoints.append([p['lat'], p['lon']])

        # create a LineString object from the OSM way
        line = LineString(way)

        distance_delta = 0.0001
        distances = np.arange(0, line.length, distance_delta)

        try:

            points = [line.interpolate(distance) for distance in distances] + [line.boundary[1]]

            new_line = LineString(points)
            print('Len ', len(new_line.coords))
            j = 0
            ps = []
            for x,y in new_line.coords:
                print(x, y)

                if j > 0:

                    print('Point' , x, ' ', y)
                    fro = (oldX, oldY)
                    to = (x, y)

                    bearing = computeBearing(fro, to)
                    p1 = computePointOnField(fro, (bearing + 90)%360 , 50)
                    p2 = computePointOnField(fro, (bearing + 270)%360 , 50)
                    print("P1 ", p1)
                    fieldPoints1.append((p1[0], p1[1], (bearing + 90)%360))
                    fieldPoints2.append((p2[0], p2[1], (bearing + 270)%360))

                    ps.append((x,y))
                    roadPoints.append((x, y, bearing, p1[0], p1[1], p2[0], p2[1]))

                j+=1
                oldX = x
                oldY = y

        except:

            if line.length <= smallest:
                smallest = line.length

            continue


print('Smallest: ', smallest)

np.savetxt("roadPoints.csv", roadPoints, delimiter=",", fmt='%f', header="x,y,b,x1,y1,x2,y2", comments='')
# np.savetxt("fieldPoints1.csv", fieldPoints1, delimiter=",", fmt='%f', header="x,y,b", comments='')
# np.savetxt("fieldPoints2.csv", fieldPoints2, delimiter=",", fmt='%f', header="x,y,b", comments='')

np.savetxt("OGroads.csv", originalPoints, delimiter=",", fmt='%f', header="x,y", comments='')

print('Time taken: ', time.time() - start_time)
