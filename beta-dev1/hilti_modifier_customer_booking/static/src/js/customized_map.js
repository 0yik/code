odoo.define('hilti_modifier_customer_booking.hilti_modifier_customer_booking', function (require) {
    "use strict";
    $(document).ready(function(){
                var pageURL = $(location).attr("pathname");
                var getURL = $(location).attr("href");
                if (pageURL == "/map_for_mobile"){
                    $("#wrapwrap").find("header").addClass('hidden');
                    $("#wrapwrap").find("footer").addClass('hidden');

                    var url = new URL(getURL);
                    var latitude = url.searchParams.get("latitude");
                    var longitude = url.searchParams.get("longitude");
                    var address = url.searchParams.get("address");
                    if(address==null){
                        address="Your Location"
                    }
                    if(latitude == null || longitude == null){
                        if(latitude == null && longitude != null){
                            var longitude = 103.777418;
                        }
                        if(latitude != null && longitude == null){
                            var latitude = 1.2828091;
                        }
                        if(latitude == null && longitude == null){
                            var longitude = 103.777418;
                            var latitude = 1.2828091;
                            address = "Default location is HILTI Office"
                        }
                    }
                    var opts = {
                        zoom: 11,
                        center: new GeoPoint(longitude, latitude),
                        enableDefaultLogo: false,
                        showCopyright: false
                    };
                    map = new SD.genmap.Map(document.getElementById('map'), opts);

                    var icon = new SD.genmap.MarkerImage({
                        image : "/hilti_modifier_customer_booking/static/src/img/openrice_icon.png",
                        title : address,
                        iconSize : new Size(16, 24),
                        iconAnchor : new Point(7, 15),
                        infoWindowAnchor : new Point(5, 0)
                    });

                    mm = new SD.genmap.MarkerStaticManager({map:map});

                    if (latitude && longitude){
                        var geo = new GeoPoint(parseFloat(longitude), parseFloat(latitude));
                        var marker = mm.add({
                            position: geo,
                            map: map,
                            icon: icon
                        });
                        map.setCenter(marker.position, map.zoom);
//                        map.infoWindow.open(marker, address);
                    }

                    map.addLogo("/hilti_modifier_customer_booking/static/src/img/sd.jpg", {width:130, height:40}, SD.POSITION_BOTTOM_LEFT, "www.streetdirectory.com");

                    var navControl = new CompleteMapControl();
                    map.addControl(navControl);
                    navControl.setDisplay(0,false);

                    geocode = new SDGeocode(map);
                    geocode.removeMouseClick();

                    EventManager.add(map, 'mousedown', function(e) {
                        if (SD.util.getMouseButton(e) == 'RIGHT') {
                            var px = map.fromLatLngToCanvasPixel(map.viewportInfo.lastCursorLatLon);
                            var x = map.viewportInfo.lastCursorLatLon.lon.toString().substr(0, 10);
                            var y = map.viewportInfo.lastCursorLatLon.lat.toString().substr(0, 8);

                            map.infoWindow.open(px,
                                                "Is this your location ?" +
                                                " <br><input type='button' value='Yes' onclick='saveLongLat(" + x + "," + y + ");map.infoWindow.close();' />" +
                                                " <input type='button' value='No' onclick='map.infoWindow.close();'>");

                            map.infoWindow.visible = false;
                            map.infoWindow.marker = null;
                        }
                    });
                }
                else{
                    $("#wrapwrap").find("header").removeClass('hidden');
                    $("#wrapwrap").find("footer").removeClass('hidden');
                }
    });
});