odoo.define('pos_pin_number.pin_number', function (require) {
"use strict";
var PopupWidget = require('point_of_sale.popups');
var PosUsernameWidget = require('point_of_sale.chrome');
var PosTableWidget = require('pos_restaurant.floors');
var gui = require('point_of_sale.gui');
var ajax = require('web.ajax');
var core = require('web.core');
var Model = require('web.Model');
var _t = core._t;


var NumberPopupWidget = PopupWidget.extend({
    template: 'NumberPopupWidget',
    show: function(options){
        options = options || {};
        this._super(options);

        this.inputbuffer = '' + (options.value   || '');
        this.decimal_separator = _t.database.parameters.decimal_point;
        this.renderElement();
        this.firstinput = true;
    },
    click_numpad: function(event){
        var newbuf = this.gui.numpad_input(
            this.inputbuffer, 
            $(event.target).data('action'), 
            {'firstinput': this.firstinput});

        this.firstinput = (newbuf.length === 0);

        if (newbuf !== this.inputbuffer) {
            this.inputbuffer = newbuf;
            this.$('.value').text(this.inputbuffer);
        }
    },
    click_confirm: function(){
        this.gui.close_popup();
        if( this.options.confirm ){
            this.options.confirm.call(this,this.inputbuffer);
        }
    },
});
PosTableWidget.TableWidget.include({
        get_pin_number: function(floorplan, table){
            var self = this;
            var user = this.pos.user.id;
            var table = this.table;
            var pin = $('.popup-input').text().split(' ')[0].trim();
            var username = $('.username')
            var model = new Model('res.users');
            var dom = []
            var error = 0
            if (!$('.popup-input').html().trim().length){
                alert("Please enter the PIN first!");
            }
            else{
                var cashier = this.pos.check_pin_number(pin);
                if(cashier){
                    floorplan.pos.set_table(table);
                    self.pos.set_cashier(cashier);
                    username.text(cashier.name)
                }else{
                    alert("You have entered a wrong PIN")
                }
                // model.call("search_read", [dom, ['pin_number', 'name']]).then(function (result) {
                //     for (var i = 0; i < result.length; i++){
                //         if (result[i].pin_number == pin && user == result[i].id){
                //                 floorplan.pos.set_table(table);
                //                 self.pos.set_cashier(result[i]);
                //                 username.text(result[i].name)
                //                 return
                //         }
                //         else{
                //                 error = 1
                //         }
                //     }
                //     if (error == 1){
                //             alert("You have entered a wrong PIN")
                //     }
                // });
            }
        },

        click_handler: function(){
            var self = this;
            var floorplan = this.getParent();
            if (floorplan.editing) {
                setTimeout(function(){  // in a setTimeout to debounce with drag&drop start
                    if (!self.dragging) {
                        if (self.moved) {
                            self.moved = false;
                        } else if (!self.selected) {
                            self.getParent().select_table(self);
                        } else {
                            self.getParent().deselect_tables();
                        }
                    }
                },50);
            }
            else {
                var self = this;
                if (!floorplan.pos.order_to_transfer_to_different_table){
                        this.gui.show_popup('number', {
                            'title':  _t('Enter PIN Number'),
                            'cheap': true,
                            'value': '',
                            'confirm': function(value) {
                                        self.get_pin_number(floorplan, this.table)
                            },
                        });
                }
                else {
                        floorplan.pos.set_table(this.table);
                }
            }
            },
    });

    var models = require('point_of_sale.models');
    models.load_fields('res.users', 'pin_number');
    // var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        check_pin_number: function (pin) {
            pin = pin.trim();
            var result = false;
            this.users.forEach(function (item) {
                if(pin == item.pin_number)result = item;
            });
            return result;
        },
    });

    PosUsernameWidget.UsernameWidget.include({
        click_username: function(){
        var self = this;
        /*this.gui.select_user({
            'security':     true,
            'current_user': this.pos.get_cashier(),
            'title':      _t('Change Cashier'),
        }).then(function(user){
            self.pos.set_cashier(user);
            self.renderElement();
        });*/
    },
});
});
