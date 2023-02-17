
// The input image to reduce, in this case an SRTM elevation map.
var dataset = ee.Image('USGS/GFSAD1000_V1').select('landcover');

// The region to reduce within.

var roads = ee.FeatureCollection('projects/ee-laguarta/assets/roadPoints');



var cropMaskVis = {
  min: 0.0,
  max: 5.0,
  opacity:0.4,
  palette: ['black', 'orange', 'brown', '02a50f', 'green', 'yellow'],
};


// Map.addLayer(dataset, cropMaskVis, 'Crop Mask');

var roadsBuff = roads.map(function (feature) {
  return feature.buffer(5, 1)
});


Map.addLayer(roadsBuff.draw({color: 'FF0000', strokeWidth: 0}), {opacity: 0.5}, "Equi Roads");



// Reduce the image within the given region, using a reducer that
// computes the max pixel value.  We also specify the spatial
// resolution at which to perform the computation, in this case 200
// meters.

var dataset = ee.ImageCollection("ESA/WorldCover/v100").first();
print(dataset);
var visualization = {
  bands: ['Map'],
  palette: ['black', 'f096ff']
};

var cropCover = dataset.eq(40)
var treeCover = dataset.eq(10)


Map.addLayer(cropCover, {min:0, max:1},  "Cropland");
Map.addLayer(treeCover, {min:0, max:1},  "Tree Cover");


var cropsum = cropCover.reduceRegions({
  collection: roadsBuff,
  reducer: ee.Reducer.sum(),
  scale: 10,
  tileScale: 5
});

var treesum = treeCover.reduceRegions({
  collection: roadsBuff,
  reducer: ee.Reducer.sum(),
  scale: 10,
  tileScale: 5
});

cropsum = cropsum.filter(ee.Filter.gt('sum', 0))
Map.addLayer(cropsum.draw({color: '0000FF', strokeWidth: 0}), {opacity: 0.5}, "CropCover Roads");


treesum = treesum.filter(ee.Filter.gt('sum', 0))
Map.addLayer(treesum.draw({color: '00FF00', strokeWidth: 0}), {opacity: 0.5}, "TreeCover Roads");

Export.table.toDrive({
    collection: cropsum,
    description: 'OverlappedLandCoverRoadsThailandESA-WorldCover-sides20x20'
});

Export.table.toDrive({
    collection: treesum,
    description: 'OverlappedTreeCoverRoadsThailandESA-WorldCover-sides20x20'
});
