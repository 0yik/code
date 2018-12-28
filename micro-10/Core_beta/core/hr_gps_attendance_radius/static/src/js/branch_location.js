
odoo.define("hr_gps_attendance_radius.get_branch_location", function (require) {
    "use strict";


    var MyAttendanceswidget = require('web_map.FieldMap');
    var Widget = require('web.Widget');

    MyAttendanceswidget.FieldMap.include({
        render_value: function() {
        if(this.get_value()) {
            this.marker.setPosition(JSON.parse(this.get_value()).position);
            this.map.setCenter(JSON.parse(this.get_value()).position);
            this.map.setZoom(JSON.parse(this.get_value()).zoom);
            this.marker.setMap(this.map);

            if (JSON.parse(this.get_value()).branchposition){
                var myLatlng = new google.maps.LatLng(JSON.parse(this.get_value()).branchposition.lat,JSON.parse(this.get_value()).branchposition.lng);
                var mapOptions = {
                  zoom: 16,
                  center: myLatlng
                }
                var markerr = new google.maps.Marker({
                    position: myLatlng,
                    title:"Branch - Company Location",
                    icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',

                });
                setTimeout(markerr.setMap(this.map), 5000);
//                markerr.setMap(this.map);
            }

        } else {
            this.marker.setPosition({lat:0,lng:0});
            this.map.setCenter({lat:0,lng:0});
            this.map.setZoom(2);
            this.marker.setMap(null);
        }
        },
    });

});