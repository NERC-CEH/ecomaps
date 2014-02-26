/**
 * Created by Phil Jenkins (Tessella) on 2/25/14.
 */

var EcomapsMap = (function() {

    var map = null;
    var layerDict = new Object();
    var defaultLayerOptions = {
        isBaseLayer: false,
        buffer: 0
    };

    var currentLayerIndex = 1;

    var initHandlers = function(){

        $("a.dataset").click(loadDataset);

        var layerContainer = $("div#options-panel");

        layerContainer.on("click", "input.layer-toggle", function(){
           toggleLayerDisplay($(this).data("layerid"));
        });

        layerContainer.on("change", "select.style-list", function(){

           setLayerStyle($(this).data("layerid"), $(this).val());
        });

        layerContainer.on("click", "a.view-analysis", function(){

            $("div#analysis-detail").load( '/analysis/view/' + $(this).data("analysisid") + '?compact' );
        });
    };

    var loadDataset = function() {

        $("li.active").removeClass("active");
        $(this).closest("li").toggleClass("active");

        setLoadingState(true);

        for(var l in layerDict) {
            removeLayerFromMap(l);
        }

        // Let's get some layers!
        var datasetId = $(this).data("dsid");

        $("div#options-panel").load('/viewdata/layers/' + datasetId + '?' + new Date().getTime(), function() {
                $("div#options-panel").show();
            }
        );

        $.getJSON('/viewdata/get_layer_data?dsid=' + datasetId,
            function(data){

                for(var i=0; i< data.length; i++){

                    var layerId = "" + datasetId + data[i].name;

//                    var layerName = data[i].title;
//                    layerList.append($("<li class='layer'>" +
//                                            "<label class='checkbox'>" +
//                                            "<input type='checkbox' checked='checked' data-layerid='" + layerId + "' class='layer-toggle' />" + layerName +
//                                        "</label></li>"));
//
//
//                    // Now add the styles for this layer...
//                    var styleList = $("<select class='style-list input-medium' data-layerid='"+ layerId +"'></select>");
//
//                    for(var j=0; j< data[i].styles.length;j++){
//
//                        styleList.append($("<option value='" + data[i].styles[j].name + "'>" + data[i].styles[j].name + "</option>"));
//                    }
//
//                    layerList.append($("<li class='layer style'>Style: </li>").append(styleList));

                    layerDict[layerId] = {
                        index: currentLayerIndex,
                        data: data[i],
                        visible: true,
                        wmsObject: null
                    };

                    addLayerToMap(layerId);
                    setLayerStyle(layerId, data[i].styles[0].name);
                }
                setLoadingState(false);
            }
        ) .fail(function() {
                alert("Something went wrong");
                setLoadingState(false);
            });
    };

    var initMap = function() {

        map = new OpenLayers.Map('map');
        map.addControl(new OpenLayers.Control.LoadingPanel());
        var lat = 54;
        var lon = -2;
        var zoom = 0;

        var position = new OpenLayers.LonLat(lon, lat);

        var wms = new OpenLayers.Layer.WMS( "OpenLayers WMS",
            "http://vmap0.tiles.osgeo.org/wms/vmap0", {layers: 'basic'} );
        map.addLayer(wms);
        map.zoomToMaxExtent();

        map.setCenter(position, 6);

        $("#map").height($("#wrap").height());
    };

    var setLoadingState = function(isLoading) {

        if(isLoading) {

            $("div#map-loading").show();
        }
        else {
            $("div#map-loading").hide();
        }
    };

    var removeLayerFromMap = function(layerId) {

        var layerObj = layerDict[layerId];
        map.removeLayer(layerObj.wmsObject);
        delete layerDict[layerId];
        currentLayerIndex--;
    };

    var addLayerToMap = function(layerId) {

        // Extract the bits we need to make the WMS object that
        // OpenLayers expects
        var layerObj = layerDict[layerId];

        var data = layerObj.data;

        var defaultLayerParams = {
            format: 'image/png',
            version: '1.3.0',
            CRS: 'CRS:84',
            transparent: 'TRUE'
        };

        var mapUrl = data.getMapUrl;
        var wmsVersion = data.wmsVersion;
        var layerName = data.name;

        if (wmsVersion) {
            defaultLayerParams.version = wmsVersion;
        }

        var layer = new OpenLayers.Layer.WMS(layerName,
            mapUrl, defaultLayerParams, defaultLayerOptions);

        layer.params['layers'] = layerName;
        map.addLayer(layer);
        layerObj.wmsObject = layer;
        currentLayerIndex++;
    };

    var toggleLayerDisplay = function(layerId) {
        var layerObj = layerDict[layerId];

        var index = layerObj.index;
        layerObj.visible = !layerObj.visible;
        //map.layers[index].mergeNewParams({styles:'boxfill/redblue'});
        map.layers[index].setVisibility(layerObj.visible);
    };

    var setLayerStyle = function(layerId, style) {

        var layerObj = layerDict[layerId];
        var index = layerObj.index;

        map.layers[index].mergeNewParams({
           'styles' : style
        });
    };

    return {

        init: function() {
            setLoadingState(false);
            initHandlers();
            initMap();
        }
    }
})();
$(function() {
        EcomapsMap.init();
    }
);
