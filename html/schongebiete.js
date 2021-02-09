var map = L.map('map').setView([47.86, 12], 10);
map.attributionControl.setPosition('bottomleft');

var l_osm = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom : 19,
    id: "l_osm",
    attribution : 'Map data &copy; <a href="http://www.openstreetmap.org">OpenStreepMap</a> contributors'
});
map.addLayer(l_osm);

var wmsLayer = L.tileLayer.betterWms("https://www.xctrails.org/geoserver/schongebiete/wms", {
    layers: 'schongebiete:geojson',
    format: 'image/png',
    styles: 'schongebiete-full-pgis',
    transparent: true
});
map.addLayer(wmsLayer);	

var wmsLayerWays = L.tileLayer.betterWms("https://www.xctrails.org/geoserver/schongebiete/wms", {
    layers: 'schongebiete:geojsonways',
    format: 'image/png',
    styles: 'schongebiete-ways-pgis',
    transparent: true
});

var overlays = {
    "Wege in Schongebieten": wmsLayerWays
};    
L.control.layers(null, overlays, {position: "topleft"}).addTo(map);
wmsLayerWays.on('add', function(e) {
    document.querySelectorAll('#wegeLegende').forEach(element => {
        element.style.display = "block";
    }); 
});
wmsLayerWays.on('remove', function(e) {
    document.querySelectorAll('#wegeLegende').forEach(element => {
        element.style.display = "none";
    }); 
});

var sidebar = L.control.sidebar({
    autopan: false,
    closeButton: true,
    container: 'sidebar',
    position: 'right',
}).addTo(map);
sidebar.open("home");

fetch("data/statistics.json")
  .then(response => response.json())
  .then(json => {
      var total = 0
      json.typeStats.forEach(t => {
        var key = Object.keys(t)[0];
        var value = t[key]
        total += parseInt(value)
        document.querySelector('#'+key).innerHTML = value;
      });
      document.querySelector('#total').innerHTML = total;
      document.querySelector('#multitypes').innerHTML = json.multiTypes.length;
      document.querySelector('#unclassifieds').innerHTML = json.unclassifieds.length;

      var unClass = document.getElementById("unclassHtml");
      var ul = document.createElement("ul");
      json.unclassifieds.forEach(t => {
        var li = document.createElement("li");
        li.innerHTML = "<a target='osm' href='https://www.openstreetmap.org/"+t+"'>"+t+"</a>";
        ul.appendChild(li);
      });
      unClass.appendChild(ul);

      var multiClass = document.getElementById("multiClassHtml");
      var ul = document.createElement("ul");
      json.multiTypes.forEach(t => {
        var li = document.createElement("li");
        var key = Object.keys(t)[0];
        var value = t[key]
        li.innerHTML = key+" "+value;
        ul.appendChild(li);
      });
      multiClass.appendChild(ul);

  });