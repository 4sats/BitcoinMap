import 'ol/ol.css';
import KML from 'ol/format/KML';
import Map from 'ol/Map';
import Stamen from 'ol/source/Stamen';
import VectorSource from 'ol/source/Vector';
import View from 'ol/View';
import {Circle as CircleStyle, Fill, Stroke, Style} from 'ol/style';
import {Tile as TileLayer, Vector as VectorLayer} from 'ol/layer';
import {transform} from 'ol/proj';

const styleCache = {};
const styleFunction = function (feature) {
  // 2012_Earthquakes_Mag5.kml stores the magnitude of each earthquake in a
  // standards-violating <magnitude> tag in each Placemark.  We extract it from
  // the Placemark's name instead.
  //const name = feature.get('name');
  //const magnitude = parseFloat(name.substr(2));
  const radius = 10;
  let style = styleCache[radius];
  if (!style) {
    style = new Style({
      image: new CircleStyle({
        radius: radius,
        fill: new Fill({
          color: 'rgba(255, 153, 0, 0.4)',
        }),
        stroke: new Stroke({
          color: 'rgba(255, 204, 0, 0.2)',
          width: 1,
        }),
      }),
    });
    styleCache[radius] = style;
  }
  return style;
};

const vector = new VectorLayer({
  source: new VectorSource({
    url: 'data/kml/export2.kml',
    format: new KML({
      extractStyles: false,
    }),
  }),
  style: styleFunction,
});

const raster = new TileLayer({
  source: new Stamen({
    layer: 'toner',
  }),
});

const map = new Map({
  layers: [raster, vector],
  target: 'map',
  view: new View({
    center: [0, 0],
    zoom: 2,
  }),
});

const info = $('#info');
info.tooltip({
  animation: false,
  trigger: 'manual',
});

const displayFeatureInfo = function (pixel) {
  info.css({
    left: pixel[0] + 'px',
    top: pixel[1] - 15 + 'px',
  });
  const feature = map.forEachFeatureAtPixel(pixel, function (feature) {
    return feature;
  });
  if (feature) {
    info.attr('data-original-title', feature.get('name')).tooltip('show');
  } else {
    info.tooltip('hide');
  }
};

const clickFeatureInfo = function (pixel) {
  info.css({
    left: pixel[0] + 'px',
    top: pixel[1] - 15 + 'px',
  });
  const feature = map.forEachFeatureAtPixel(pixel, function (feature) {
    return feature;
  });
  if (feature) {
    const fet = feature.clone();
    const coordinate = fet.getGeometry().transform('EPSG:3857', 'EPSG:4326').getCoordinates();
    const coordinates = coordinate.toString().split(",");
    map.getView().setCenter(transform([coordinates[0], coordinates[1]], 'EPSG:4326', 'EPSG:3857'));
    map.getView().getZoom()<15 ? map.getView().setZoom(map.getView().getZoom() + 3):"";
    console.log(map.getView().getZoom())
    info.tooltip('hide');
    $("#header").html(feature.get("name"));
    $("#body").html(
      "<p>"+feature.get("description")+'<br> <a href="https://www.openstreetmap.org/#map=19/'+coordinates[1]+'/'+coordinates[0]+'" target="_blank">Open in OSM</a>'
      +'<br> <a href="https://maps.google.com/?q='+coordinates[1]+','+coordinates[0]+'" target="_blank">Open in Google Maps</a>'
      +"</p>"
    );
    $("#myModal").modal();
  } else {
    info.tooltip('hide');
  }
};

map.on('pointermove', function (evt) {
  if (evt.dragging) {
    info.tooltip('hide');
    return;
  }
  displayFeatureInfo(map.getEventPixel(evt.originalEvent));
});

map.on('click', function (evt) {
  clickFeatureInfo(evt.pixel);
});
