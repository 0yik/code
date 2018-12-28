odoo.define('pos_show_seat_number.pos_show_seat_number', function (require) {
    "use strict";

    var devices = require('point_of_sale.devices');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var OptionsPopupWidget = require('pizzahut_modifier_startscreen.pizzahut_modifier_startscreen');
    var _t = core._t;
    var Model = require('web.DataModel');
    var models = require('point_of_sale.models');
    var Orderline = models.Orderline.prototype;
    var gui = require('point_of_sale.gui');
    var pos_floor = require('pos_restaurant.floors');
    var assign_temp_order_pos = require('assign_temp_order.pos');
    var QWeb = core.qweb;
    var Order = models.Order.prototype;
    var PosTableWidget = require('pos_restaurant.floors');
    var NumberPopupWidget = require('point_of_sale.popups');

    var SeatsPopupWidget = NumberPopupWidget.extend({
        template: 'NumberSeatPopupWidget',
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
        }
    });
    gui.define_popup({name:'number_seats', widget: SeatsPopupWidget});

    OptionsPopupWidget.include({
        events: _.extend({}, OptionsPopupWidget.prototype.events, {
             'click .button.dive_in':  'display_popup_guest',
        }),
        show_pop_up: function () {
            var self = this;
            this.gui.show_popup('number_seats', {
                'title': _t('Guests?'),
                'cheap': true,
                'value': '',
                'confirm': function (value) {
                    var flag = self.dive_in_order_category();
                    if (flag) {
                        self.show_pop_up();
                    }
                },
                'cancel': function () {
                    alert("Please enter the number of Guests first!");
                    self.show_pop_up();
                }

            });
        },
        display_popup_guest: function () {
            this.show_pop_up();
        },
        dive_in_order_category: function () {
            var self = this.pos;
            var number_of_seat = $('.popup-input-seat').html().trim();
            if (!number_of_seat.length || number_of_seat === '0') {
                alert("Please enter the number of Guests first!");
                return true;
            }
            self.number_of_seat = parseInt(number_of_seat);
            $('.assign-order').removeClass('oe_hidden');
            this.pos.category = "dive_in";
            self.popup_option = 'Dine In';
            // this.pos.category = "dive_in";
            this.pos.all_free = false;
            this.pos.is_staff_meal = false;
            this.pos.dine_is_assign_order = false;
            // Fix: To show where it comes from In KDS screen
            var def = new $.Deferred();
            var fields = _.find(this.pos.models, function (model) {
                return model.model === 'product.product';
            }).fields;
            var model = new Model('pos.order.category');
            // self.db.product_by_id = {};
            self.db.product_by_category_id = {};
            $('button.take_away_dinein').removeClass('oe_hidden');
            var $CreateSalesOrderbutton = $('.CreateSalesOrderbutton');
            if (this.pos.category == 'dive_in' && $CreateSalesOrderbutton) {
                $CreateSalesOrderbutton.addClass('oe_hidden');
            }
            model.call("get_current_category", ['Dine In', fields, this.pos.pricelist.id]).then(function (result) {
                if (result != 0) {
                    if (result == 1) {
                        self.gui.screen_instances['products'].product_list_widget.product_list = [];
                        self.db.add_products([]);
                    } else {
                        self.db.add_products(result);
                        self.gui.screen_instances['products'].product_list_widget.set_product_list(result);
                        self.gui.screen_instances['products'].product_list_widget.renderElement();
                    }
                } else {
                    alert("Wrong Product Order Category Defined")
                }
            });
            if (!self.config.iface_floorplan) {
                self.floors = []
                // self.floors_by_id = {};

                for (var i = 1; i <= Object.keys(self.floors_all_by_id ? self.floors_all_by_id : []).length; i++) {
                    if (self.floors_all_by_id[i].id == self.config.floor_ids[0]) {
                        self.floors.push(self.floors_all_by_id[i])
                    }

                    self.floors_by_id[self.floors_all_by_id[i].id] = self.floors_all_by_id[i];
                }
                if (self.floors && self.floors.length > 0 && !self.floors[0].tables.length) {
                    self.floors[0].tables = []
                    for (var i = 0; i < Object.keys(self.floors[0].table_ids).length; i++) {
                        self.floors[0].tables.push(self.tables_by_id[self.floors[0].table_ids[i]])
                    }
                }
                self.config.iface_floorplan = 1;
                self.iface_floorplan = 1;
                this.gui.set_startup_screen('floors');
                this.gui.show_screen('floors');
                self.trigger('update:floor-screen');
            }
            else {
                this.gui.show_screen('floors');
            }
        }
    });
    PosTableWidget.TableWidget.include({
        click_handler: function () {
            var self = this;
            var current_guess = self.pos.number_of_seat;
            var current_seats = self.table .seats;
            if (current_guess > current_seats){
                this.gui.show_popup('error', {
                    title: _t('Warning'),
                    body: _t('Seat Number should be greather than guest number.')
                });
                return false;
            }
            var floorplan = this.getParent();
            if (floorplan.editing) {
                setTimeout(function() {
                    if (!self.dragging) {
                        if (self.moved) {
                            self.moved = false;
                        } else if (!self.selected) {
                            self.getParent().select_table(self);
                        } else {
                            self.getParent().deselect_tables();
                        }
                    }
                }, 50);
            } else {
                floorplan.pos.set_table(this.table);
            }
        }
    });

});
