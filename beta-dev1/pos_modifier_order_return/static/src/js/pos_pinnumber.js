odoo.define('pos_pin_number.pinnumber', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var QWeb = core.qweb;
    var Model = require('web.Model');

    for (var index in gui.Gui.prototype.popup_classes) {
        if(gui.Gui.prototype.popup_classes[index].name=='number'){
            var NumberWidget = gui.Gui.prototype.popup_classes[index].widget;
            var PinNumberWidget = NumberWidget.extend({
                template: 'PinNumberWidget',
                title:  'Enter PIN Number',
                click_confirm: function(){
                    var self = this;
                    this.gui.close_popup();
                    var res_user = new Model('res.users');
                    res_user.call("check_pos_security_pin_number", [this.inputbuffer]).then(function (value) {
                        if(value){
                            if( self.options.after_certain ){
                                self.options.after_certain.call(self);
                            }
                        }else{
                            alert('Incorrect Pin Number');
                        }
                    });
                },
            });
            gui.define_popup({name:'pin_number', widget: PinNumberWidget});
            break;
        }
    }

});