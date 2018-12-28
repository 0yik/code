
odoo.define("meeting_gps.get_current_location", function (require) {
    "use strict";
    var form_widget = require('web.form_widgets');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    var Model = require('web.Model');


    function getLocation(event_id, sign_in_out) {

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                 var custom_model = new Model('calendar.event')
                 if (sign_in_out == "sign_in"){
                    custom_model.call('get_sign_in_location',[position.coords.latitude, position.coords.longitude, event_id])
                 }
                 if (sign_in_out == "sign_out"){
                    custom_model.call('get_sign_out_location',[position.coords.latitude, position.coords.longitude, event_id])
                 }
                 window.location.reload();
                }, errorFunction);
        } else {
            alert("Geolocation is not supported by this browser!");
        }
    }

    function errorFunction(err) {
        alert("Allow get location to this site");
    }

    form_widget.WidgetButton.include({
        on_click: function() {
             if(this.node.attrs.custom === "click"){
                getLocation(this.view.datarecord.id, 'sign_in');
                return;
             }
             if(this.node.attrs.custom === "click_sign_out"){
                getLocation(this.view.datarecord.id, 'sign_out');
                return;
             }
             this._super();
        },
    });
});