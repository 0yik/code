odoo.define('branch_link_googlemaps.google_map', function (require) {
    "use strict";

    var FormView = require("web.FormView");
    var Model = require('web.Model');

    FormView.include({
        on_button_new: function() {
            var self = this;
            self._super.apply(this, arguments);
            var script = window.document.createElement('script');
            script.innerHTML = `
                var placeSearch, autocomplete;
                      var componentForm = {
                        street_number: 'short_name',
                        route: 'long_name',
                        locality: 'long_name',
                        administrative_area_level_1: 'short_name',
                        country: 'long_name',
                        postal_code: 'short_name'
                      };

                      function initAutocomplete() {
                        console.log('initAutocomplete');
                        // Create the autocomplete object, restricting the search to geographical
                        // location types.
                        autocomplete = new google.maps.places.Autocomplete(
                            (document.getElementsByName("address")[0]),
                            {types: ['geocode']});

                        // When the user selects an address from the dropdown, populate the address
                        // fields in the form.
                        autocomplete.addListener('place_changed', fillInAddress);
                      }

                      function fillInAddress() {
                        // Get the place details from the autocomplete object.
                        var place = autocomplete.getPlace();
                        console.log('Place', place);
                        let result = place.address_components;
                        if(result){
                        $('.street_auto_fill').val('');
                        $('.postcode_auto_fill').val('');
                        for(let i =0; i < result.length; i++){
                            if(result[i].types[0] == 'street_number'){
                            }
                            if(result[i].types[0] == 'route'){
                                $('.street_auto_fill').val(result[i]['long_name']);
                            }
                            if(result[i].types[0] == 'locality' || result[i].types[0] == 'administrative_area_level_1'){
                            }
                            if(result[i].types[0] == 'country'){
                            }
                            if(result[i].types[0] == 'postal_code'){
                                $('.postcode_auto_fill').val(result[i]['long_name']);
                            }
                        }
                        }
                      }

                      // Bias the autocomplete object to the user's geographical location,
                      // as supplied by the browser's 'navigator.geolocation' object.
                      function geolocate() {
                        if (navigator.geolocation) {
                          navigator.geolocation.getCurrentPosition(function(position) {
                            var geolocation = {
                              lat: position.coords.latitude,
                              lng: position.coords.longitude
                            };
                            var circle = new google.maps.Circle({
                              center: geolocation,
                              radius: position.coords.accuracy
                            });
                            autocomplete.setBounds(circle.getBounds());
                          });
                        }
                      };
                `;
            script.setAttribute('type', 'text/javascript');
            $( "body" ).append(script);

            var ga = window.document.createElement('script');
            ga.setAttribute('type', 'text/javascript');
            ga.setAttribute('async', true);
            ga.setAttribute('defer', true);
            ga.setAttribute("src", 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCmDx-O5RaDUcJsiKgfThsIvaB_VdSl_Ec&libraries=places&callback=initAutocomplete');
            var s = document.getElementsByTagName('script')[0];
            ga.onload = function() {
              alert("Script loaded and ready");
            };
            $("body" ).append(ga);
        },
        on_button_edit: function() {
            var self = this;
            self._super.apply(this, arguments);
            var script = window.document.createElement('script');
            script.innerHTML = `
                var placeSearch, autocomplete;
                      var componentForm = {
                        street_number: 'short_name',
                        route: 'long_name',
                        locality: 'long_name',
                        administrative_area_level_1: 'short_name',
                        country: 'long_name',
                        postal_code: 'short_name'
                      };

                      function initAutocomplete() {
                        console.log('initAutocomplete');
                        // Create the autocomplete object, restricting the search to geographical
                        // location types.
                        autocomplete = new google.maps.places.Autocomplete(
                            (document.getElementsByName("address")[0]),
                            {types: ['geocode']});

                        // When the user selects an address from the dropdown, populate the address
                        // fields in the form.
                        autocomplete.addListener('place_changed', fillInAddress);
                      }

                      function fillInAddress() {
                        // Get the place details from the autocomplete object.
                        var place = autocomplete.getPlace();
                        console.log('Place', place);
                        let result = place.address_components;
                        if(result){
                        $('.street_auto_fill').val('');
                        $('.postcode_auto_fill').val('');
                        for(let i =0; i < result.length; i++){
                            if(result[i].types[0] == 'street_number'){
                            }
                            if(result[i].types[0] == 'route'){
                                $('.street_auto_fill').val(result[i]['long_name']);
                            }
                            if(result[i].types[0] == 'locality' || result[i].types[0] == 'administrative_area_level_1'){
                            }
                            if(result[i].types[0] == 'country'){
                            }
                            if(result[i].types[0] == 'postal_code'){
                                $('.postcode_auto_fill').val(result[i]['long_name']);
                            }
                        }
                        }
                      }

                      // Bias the autocomplete object to the user's geographical location,
                      // as supplied by the browser's 'navigator.geolocation' object.
                      function geolocate() {
                        if (navigator.geolocation) {
                          navigator.geolocation.getCurrentPosition(function(position) {
                            var geolocation = {
                              lat: position.coords.latitude,
                              lng: position.coords.longitude
                            };
                            var circle = new google.maps.Circle({
                              center: geolocation,
                              radius: position.coords.accuracy
                            });
                            autocomplete.setBounds(circle.getBounds());
                          });
                        }
                      };
                `;
            script.setAttribute('type', 'text/javascript');
            $( "body" ).append(script);

            var ga = window.document.createElement('script');
            ga.setAttribute('type', 'text/javascript');
            ga.setAttribute('async', true);
            ga.setAttribute('defer', true);
            ga.setAttribute("src", 'https://maps.googleapis.com/maps/api/js?key=AIzaSyCmDx-O5RaDUcJsiKgfThsIvaB_VdSl_Ec&libraries=places&callback=initAutocomplete');
            var s = document.getElementsByTagName('script')[0];
            ga.onload = function() {
              alert("Script loaded and ready");
            };
            $("body" ).append(ga);
        },
    });
});
