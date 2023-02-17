import requests
import numpy as np
import time
import shutil

start_time = time.time()

import pandas as pd
import csv
import urllib.request, os
import urllib.parse
import numpy as np
import streetview
import math


KEY = """ YOUR Google API KEY - See Google Street View Static API documentation to generate your own key"""
key = "&key=" + KEY


LANDCOVER_FILENAME = 'data/OverlappedLandCoverRoadsThailandESA-WorldCover-sides20x20.csv'
TREECOVER_FILENAME = 'data/OverlappedTreeCoverRoadsThailandESA-WorldCover-sides20x20.csv'


crops = pd.read_csv(LANDCOVER_FILENAME)
print(crops.columns)
crops = crops.rename(columns={'system:index': 'ID', '.geo':'geo'})

trees = pd.read_csv(TREECOVER_FILENAME)
trees = trees.rename(columns={'system:index': 'ID', '.geo':'geo'})

old_len = len(crops)
removedCrops = (crops[crops.ID.isin(trees.ID)])
crops = (crops[~crops.ID.isin(trees.ID)])
print(crops[0:10])
print(len(removedCrops))

print('Crop Points removed due to trees is ',(old_len - len(crops)), ' out of ', old_len, ' candidate crop points.' )

def checkInGrowing(date):
    MONTHS = '05, 06, 07, 08, 09'
    if date[-2:] in MONTHS:
        print(date[-2:])
        return True
    else:
        return False

def getStreet(lat,lon,SaveLoc, bearing, meta):

  #heading indicates the compass heading of the camera. Accepted values are from 0 to 360 (both values indicating North, with 90 indicating East, and 180 South),
  #fov (default is 90) determines the horizontal field of view of the image. The field of view is expressed in degrees, with a maximum allowed value of 120
  # heading1 = (bearing + 90) % 360
  # heading2 = (bearing + 270) % 360
  heading1 = bearing
  # heading2 = (bearing + 180) % 360

  MyUrl = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location="+str(lat)+","+str(lon)+"&fov=90&heading="+str(heading1)+"&pitch=0" + key
  fi = meta +str(heading1)+ ".jpg"
  urllib.request.urlretrieve(MyUrl, os.path.join(SaveLoc,fi))
  # MyUrl = "https://maps.googleapis.com/maps/api/streetview?size=640x640&location="+str(lat)+","+str(lon)+"&fov=80&heading="+str(heading2)+"&pitch=0&key=AIzaSyDg_suLgCZ9BrfSPRxMrekQEhDsCdk6mjE"
  # fi = meta +str(heading2)+ ".jpg"
  # urllib.request.urlretrieve(MyUrl, os.path.join(SaveLoc,fi))

def computeBearing(fro, to):
    y = math.sin(to[1]-fro[1]) * math.cos(to[0])
    x = math.cos(fro[0])*math.sin(to[0]) - math.sin(fro[0])*math.cos(to[0])*math.cos(to[1]-fro[1])
    θ = math.atan2(y, x)
    brng = (θ*180/math.pi + 360) % 360
    return brng

def computeDistance(fro, to):
    #IN METERS
    R = 6371e3
    ga1 = fro[0] * math.pi/180
    ga2 = to[0] * math.pi/180
    dga = (to[0]-fro[0]) * math.pi/180
    dDel = (to[1]-fro[1]) * math.pi/180

    a = math.sin(dga/2) * math.sin(dga/2) + math.cos(ga1) * math.cos(ga2) * math.sin(dDel/2) * math.sin(dDel/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d

def computePointOnField(fro, theta, d):
    R = 6371e3
    Ad = d/R
    theta = math.radians(theta)
    la2 =  math.asin(math.sin(fro[0]) * math.cos(Ad) + math.cos(fro[0]) * math.sin(Ad) * math.cos(theta))
    lo2 = fro[1] + math.atan2(math.sin(theta) * math.sin(Ad) * math.cos(fro[0]) , math.cos(Ad) - math.sin(fro[0]) * math.sin(la2))
    return (la2,lo2)


def getCentre(lonLats):
    lon = (lonLats[0][0] + lonLats[4][0])/2
    lat = (lonLats[0][1] + lonLats[4][1])/2
    return lon, lat

def getPointfromGeo(geo):
    lonLats = []
    stIdx = geo.find('[') +2
    for i in range(7):
        edIdx = geo.find(']')
        latLon = geo[stIdx+1:edIdx]
        lon, lat = latLon.split(',')
        lonLats.append((float(lon),float(lat)))
        geo = geo[edIdx+2:]
        stIdx = geo.find('[')
    return lonLats

def getMeta(points, myloc, imLimit=0):
    uniqueImageIDs= []
    points = points.reset_index()  # make sure indexes pair with number of rows
    if imLimit == 0:
        imLimit = len(points)

    i = 0
    for idx, crop in points.iterrows():
        if i <= imLimit:
            print(crop)
            lonLats = getPointfromGeo(crop['geo'])
            lon, lat = getCentre(lonLats)
            link = "https://maps.googleapis.com/maps/api/streetview/metadata?size=640x640&location="+str(lat)+","+str(lon)+"&fov=80&heading=0&pitch=0" + key
            response = requests.get(link)
            resJson = response.json()

            bearing = float(crop['b'])
            pt1 = (float(crop['x1']), float(crop['y1']))
            pt2 = (float(crop['x2']), float(crop['y2']))
            print(bearing)
            if resJson['status'] ==  'OK':
                print('Res')
                print(resJson)
                fro = (float(lat), float(lon))
                to = (float(resJson["location"]["lat"]), float(resJson["location"]["lng"]))

                if checkInGrowing(resJson['date']):
                    if resJson['pano_id'] not in uniqueImageIDs:
                        bearing = computeBearing(fro, pt1)
                        distance = computeDistance(fro,pt1)
                        print("Distance (m) ", distance)
                        uniqueImageIDs.append(resJson['pano_id'])
                        meta = resJson['date'] + resJson['pano_id']
                        getStreet(lat,lon, myloc, bearing, meta)

                        bearing = computeBearing(fro, pt2)
                        distance = computeDistance(fro,pt2)
                        print("Distance (m) ", distance)
                        uniqueImageIDs.append(resJson['pano_id'])
                        meta = resJson['date'] + resJson['pano_id']
                        getStreet(lat,lon, myloc, bearing, meta)
        i+=1


#
# print(computeBearing(fro, to))
#
# print(computeBearing(to, fro))


# getMeta(removedCrops, 'images/removedCrops/')
imLimit = 100
getMeta(crops, 'images/noTreeCropsEmbeddedSides/', imLimit=1000)
