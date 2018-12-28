odoo.define('google_map_locator.leadMapFormWidget', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var crash_manager = require('web.crash_manager');
    var data = require('web.data');
    var datepicker = require('web.datepicker');
    var dom_utils = require('web.dom_utils');
    var Priority = require('web.Priority');
    var ProgressBar = require('web.ProgressBar');
    var Dialog = require('web.Dialog');
    var common = require('web.form_common');
    var formats = require('web.formats');
    var framework = require('web.framework');
    var Model = require('web.DataModel');
    var pyeval = require('web.pyeval');
    var session = require('web.session');
    var utils = require('web.utils');
    var form_common = require('web.form_common');
    var _t = core._t;
    var QWeb = core.qweb;
    //Widget for FormView
    var leadMapFormWidget = form_common.AbstractField.extend({
        template: 'leadmap',

        start: function(){
            var self = this;
            var r = this._super();
            var rendererOptions = {draggable: false};
            var orderId = [];
            try {
                this.directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
                this.directionsService = new google.maps.DirectionsService();
                this.map;
                this.model = this.view.dataset.model;
                this.country = new google.maps.LatLng(55, -180);

                var orderId = [];
                $('td.o_list_record_selector').each(function(i){
                    if ($(this).closest('tr').attr('data-id')){
                        orderId.push(parseInt($(this).closest('tr').attr('data-id')));
                    }
                });
            } catch(err) {

            }
            self.mapInit(orderId);
            return r;
        },
        mapInit: function(id){
            var self = this;

            this.lines = new Model('crm.lead');
            var defs = [];
            this.waypoints = [];
            if (this.model == 'crm.lead'){
                this.lines.call('search', [[['id','in',id]]])
                .then(function(results){
                    _.each(results, function(val, index){
                        defs.push(self.lines.call('read', [[val], ['city', 'country_id', 'company_id']], {})
                            .then(function(result){
                                self.waypoints.push(result[0]);
                            }));
                    });
                    $.when.apply($, defs).then(function(){
                        self.get_ltlg(self.waypoints);
                    });
                });
            }
        },

        get_ltlg: function(res){
            var self = this;
            var mapOptions = {zoom: 2, center: this.country, mapTypeId: google.maps.MapTypeId.ROADMAP};
            var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

            map.setOptions({ minZoom: 2, maxZoom: 10 });
            var geocoder =  new google.maps.Geocoder();
            var infowindow = new google.maps.InfoWindow();
            var marker, i;
            for (var i=0;i<res.length;i++){
                if (res[i].city) {
                    geocoder.geocode({ 'address': res[i].city}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            var ltlg = results[0].geometry.location.lat() + " , " +results[0].geometry.location.lng();
                        }
                        if (ltlg){
                            var location = [ltlg];
                            for (i = 0; i < location.length; i++) {
                                var loc = location[0].split(",") ;
                                marker = new google.maps.Marker({
                                    position: new google.maps.LatLng(loc[0],loc[1]),
                                    map: map
                                });
                                google.maps.event.addListener(marker, 'click', (function(marker, i) {
                                    return function() {
                                        infowindow.setContent(results[0].address_components[0].short_name + "," + results[0].address_components[2].long_name);
                                        infowindow.open(map, marker);
                                    }
                                })(marker, i));
                            }
                        }
                    });
                }
            }
        },
    });

    core.form_widget_registry.add('leadmap', leadMapFormWidget)

    var MapFormWidget = form_common.AbstractField.extend({
        template: 'map',

        start: function(){
            var self = this;
            var r = this._super();
            var rendererOptions = {draggable: false};
            var orderId = [];
            try {
                this.directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
                this.directionsService = new google.maps.DirectionsService();
                this.map;
                this.model = this.view.dataset.model;
                this.country = new google.maps.LatLng(55, -180);
                orderId = this.view.dataset.ids[0];
            } catch(err) {

            }
            self.mapInitt(orderId);
            return r;
        },
        mapInitt: function(id){
            var self = this;
            this.lines = new Model('crm.lead');
            var defs = [];
            this.waypoints = [];
            if (this.model == 'crm.lead'){
                this.lines.call('search', [[['id','in',[id]]]])
                .then(function(results){
                    _.each(results, function(val, index){
                        defs.push(self.lines.call('read', [[val], ['name','phone','city', 'country_id', 'company_id']], {})
                            .then(function(result){
                                self.waypoints.push(result[0]);
                            }));
                    });
                    $.when.apply($, defs).then(function(){
                        self.get_ltlg(self.waypoints);
                    });
                });
            }
            
        },
        get_ltlg: function(res){
            var self = this;
            var mapOptions = {zoom: 4, mapTypeId: google.maps.MapTypeId.ROADMAP};
            var map = new google.maps.Map(document.getElementById('tour-map-canvas'), mapOptions);

            //map.setOptions({ minZoom: 2, maxZoom: 10, center: this.country});
            var geocoder =  new google.maps.Geocoder();
            var infowindow = new google.maps.InfoWindow({maxWidth: 300});
            var i;
            for (var i=0;i<res.length;i++){
                if (res[i].city) {
                    geocoder.geocode({ 'address': res[i].city}, function(results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            var ltlg = results[0].geometry.location.lat() + " , " +results[0].geometry.location.lng();
                        }
                        if (ltlg){
                            this.centermap = new google.maps.LatLng(results[0].geometry.location.lat(), results[0].geometry.location.lng());
                            map.setOptions({ minZoom: 2, center: this.centermap});
                            var location = [ltlg];
                            for (i = 0; i < location.length; i++) {
                                var loc = location[0].split(",") ;
                                self.marker = new google.maps.Marker({
                                    position: new google.maps.LatLng(loc[0],loc[1]),
                                    map: map
                                });
                                google.maps.event.addListener(self.marker, 'click', (function(marker, i) {
                                    return function() {
                                        infowindow.setContent(res[i].name + "<br/>" + (res[i].phone || '') + "<br/>" + results[0].address_components[0].short_name + "," + results[0].address_components[2].long_name);
                                        infowindow.open(map, marker);
                                    }
                                })(self.marker, i));
                            }
                        }
                    });
                } 
            }
        },
        calcRoute: function(results){
            var self = this;
            var location = [];
            self.request = {
                origin:'',
                destination:'',
                waypoints:[],
                travelMode: google.maps.TravelMode.DRIVING
            };
            this.model = new Model('res.company');
            _.each(results, function(val, index){
                 if (!val.city && !val.company_id){
                    return ;
                }
                self.model.call('read', [[val.company_id[0]], ['city', 'street','zip','country_id']], {}).then(function(value){
                        var origin = val.city;
                        var destination = value[0].city;

                        if(value[0].city != false){
                            var street = value[0].city.replace(',','')
                            destination += ', ' + value[0].city;
                        }
                        if(value[0].zip != false){
                            destination += ', ' + value[0].zip;
                        }
                        if(value[0].country_id != false){
                            destination += ', ' + value[0].country_id[1];
                        }
                        self.request.origin = origin;
                        self.request.destination = destination;

                        self.request.waypoints.push({location: origin, stopover: true});
                        self.request.waypoints.push({location: destination, stopover: true});
                        if(index == results.length-1){
                            self.display();
                        };
                    });
            });

        },
        showSteps: function(response){
            var self = this;
            var output = '';
            var route = response.routes[0];

            var distance = self.computeTotalDistance(route);
            if (parseFloat(distance)){
                this.field_manager.fields['km'].set_value(parseFloat(distance.replace(',','.')));
            }
            else{
                this.field_manager.fields['km'].set_value(parseFloat(distance));
            }
            this.field_manager.fields['km']._dirty_flag = true;
            var dist_miles = parseFloat(distance) * 0.621371;
            self.$el.find('.oe_form_group').remove();
            $('#dist').html('<div><b>Distance:-</b> '+distance+ ' km <span style="color:red">('+dist_miles+' miles)</span></div>');
            $('#distance').attr('disabled','disabled');
            self.mapInit();
        },
        computeTotalDistance: function(route){
            var self = this;
            var total = 0;
            for (var i = 0; i < route.legs.length; i++){
                total += route.legs[i].distance.value;
            }
            total = total/1000;
            return total.toFixed(1).toString().replace('.',',');
        },
        display: function(){
            var self = this;
            self.directionsService.route(self.request, function(response, status) {
                if (status == google.maps.DirectionsStatus.OK) {
                     self.directionsDisplay.setDirections(response);
                }
            });
        }

    });
    core.form_widget_registry.add('map', MapFormWidget)

    return {
        leadMapFormWidget: leadMapFormWidget,
        MapFormWidget: MapFormWidget,
    };
});
