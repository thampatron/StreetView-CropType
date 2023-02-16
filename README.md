# StreetView-CropType


This repo is used to pull Google Street View (GSV) images of cropland for a user defined geographical area.

# How it works
### 1. Generating Street Points: getAllRoadPtsBearing.py
Input: **user defined area**

Output: **roadPoints.csv** file of equidistant geo-coordinates along all road points

    1. Open Street Map (OSM) ways are downloaded for the defined region using Overpass-Turbo API.
    2. Equidistant (lat,lon) points are generated along each OSM way along with point metadata on the bearing of each point along the way.
    3. Two lines of equidistant (lat,lon) points are generated 50m parallel to each way on the field, one on each side of the way. 
CSV Output Data:

    - {b} = bearing of road at that point.
    - {x1, y1} = {lat,lon} at a point 50m into the field parallel to the point on the road.
    - {x2, y2} = {lat,lon} at a point 50m into the opposite side of the field parallel to the point on the road.


### 2. Land Cover map filtering of road points on Google Eart Engine (GEE): GeeFilterPoints.js

Input: **roadPoints.csv** 

Output: 2 dicts saved in Google Drive: 
- Dict of all points in LandCover area: **OverlappedLandCoverRoadsThailandESA-WorldCover-sides20x20.csv**
- Dict of all points in TreeCover area: **OverlappedTreeCoverRoadsThailandESA-WorldCover-sides20x20.csv**

The GEE script uses the USGS GFSAD1000 dataset and is overlapped with the roadPoints generated to filter out the points that are not in a Land Cover area and saves the subset of roadPoints from the region defined that lie within land cover. 
Further, it also saves the roadPoints that lie within tree cover. This is used in the next section to remove Land Cover roadPoints that have tree cover nearby, since tree cover obstructs GSV images from showing field images.

**USER TODO:** 

    Upload roadPoints.csv to GEE by clicking top right on "Assets", then "NEW", then "CSV File". 

    IMPORTANT: When uploading the new csv asset, scroll down to "Advanced Options" and set the "X column (longitude)" to "y" and the "Y column (latitude)" to "x".



### 3. Post-processing and GSV image Querying: getGSVFieldImages.py

Input: 
- Dict of all points in LandCover area: **OverlappedLandCoverRoadsThailandESA-WorldCover-sides20x20.csv**
- Dict of all points in TreeCover area: **OverlappedTreeCoverRoadsThailandESA-WorldCover-sides20x20.csv**

Output: 
file with GSV images of Land Cover fields

    1. Loads CSV files from GEE, and filters out from the crop roadPoints those that lie in tree cover. 
    2. Makes a GSV metadata request to check where the nearest GSV image is to the roadPoint, checks if the image was taken during the defined growing season, and whether the image has already been pulled. 
    3. Calculates "heading" parameter for the GSV image request based on the GSV image location and the point on the field corresponding to the roadPoint. 
    4. Requests image from GSV and saves in **images/noTreeCropsEmbeddedSides/**. 
