odoo.define('pos_restaurant_kitchen_widget', function (require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var qweb = core.qweb;
    var syncing = require('client_get_notify');

    var KitchenScreenWidget = screens.ScreenWidget.extend({
        template: 'KitchenScreenWidget',
        show_numpad: false,
        show_leftpane: true,
        previous_screen: false,
        start: function () {
            var self = this;
            this._super();
            this.pos.bind('update:kitchenscreen', function () {
                self.renderElement();
            })
        },
        show: function () {
            var self = this;
            this._super();
        },
        render_items: function (items) {
            items.sort(function (item1, item2) {
                return Date.parse('1970/01/01 ' + item1.creation_time.slice(0, -3) + ' ' + item1.creation_time.slice(-3)) - Date.parse('1970/01/01 ' + item2.creation_time.slice(0, -3) + ' ' + item2.creation_time.slice(-3))
            });
            var render_status = null;
            for (var i = 0; i < items.length; i++) {
                var line = items[i];
                var kitchen_line = $(qweb.render('KitchenLine', {
                    widget: this,
                    line: line,
                }));
                if (line.state == 'High-Priority') {
                    this.$('.kitchen-list-priority').append(kitchen_line);
                    render_status = true;
                } else if (line.state == 'Error') {
                    this.$('.kitchen-list-error').append(kitchen_line);
                    render_status = true;
                } else if (line.state == 'Confirmed') {
                    this.$('.kitchen-list-normal').append(kitchen_line);
                    render_status = true;
                } else if (line.state == 'Waiting-delivery') {
                    this.$('.kitchen-list-waiting-delivery').append(kitchen_line);
                    render_status = true;
                } else if (line.state == 'Cancel') {
                    this.$('.kitchen-list-cancel').append(kitchen_line);
                    render_status = true;
                } else if (line.state == 'Not-enough-material') {
                    this.$('.kitchen-list-not-enough-material').append(kitchen_line);
                    render_status = true;
                }
            }
            if (render_status == true) {
                this.pos.play_sound();
            }
        },
        render_items_manager: function () {
            var orders = this.pos.get('orders').models;
            var items = [];
            for (var i = 0; i < orders.length; i++) {
                for (var j = 0; j < order.orderlines.models.length; j++) {
                    items.push(order.orderlines.models[i]);
                }
            }
            if (items.length > 0) {
                items.sort(function (item1, item2) {
                    return Date.parse('1970/01/01 ' + item1.creation_time.slice(0, -3) + ' ' + item1.creation_time.slice(-3)) - Date.parse('1970/01/01 ' + item2.creation_time.slice(0, -3) + ' ' + item2.creation_time.slice(-3))
                });
                for (var i = 0; i < items.length; i++) {
                    var line = items[i];
                    if (line.quantity != 0) {

                    }
                    var kitchen_line = $(qweb.render('KitchenLine', {
                        widget: this,
                        line: line,
                    }));
                    var render_status = null;
                    if (line.state == 'High-Priority') {
                        this.$('.kitchen-list-priority').append(kitchen_line);
                        render_status = true;
                    } else if (line.state == 'Error') {
                        this.$('.kitchen-list-error').append(kitchen_line);
                        render_status = true;
                    } else if (line.state == 'Need-to-confirm') {
                        this.$('.kitchen-list-need-to-confirm').append(kitchen_line);
                        render_status = true;
                    } else if (line.state == 'Confirmed') {
                        this.$('.kitchen-list-normal').append(kitchen_line);
                        render_status = true;
                    } else if (line.state == 'Waiting-delivery') {
                        this.$('.kitchen-list-waiting-delivery').append(kitchen_line);
                        render_status = true;
                    } else if (line.state == 'Cancel') {
                        this.$('.kitchen-list-cancel').append(kitchen_line);
                        render_status = true;
                    } else if (line.state == 'Not-enough-material') {
                        this.$('.kitchen-list-not-enough-material').append(kitchen_line);
                        render_status = true;
                    }
                    if (render_status == true) {
                        this.pos.soud_notify('done');
                    }
                }
            }
        },
        renderElement: function () {
            this._super();
            var self = this;
            console.log('scren type: ' + this.pos.config.screen_type)
            var items = [];
            if (this.pos.config.screen_type == 'manager') {
                console.log('this is future for manager control all system');
                return;
            } else {
                var orders = this.pos.get('orders').models;
                var order = null;
                var categs = [];
                for (var i = 0; i < this.pos.config.categ_ids.length; i++) {
                    categs.push(this.pos.config.categ_ids[i]);
                }
                if (categs.length <= 0) {
                    console.log('kitchen screen: Categories have not set');
                    return;
                }
                if (orders.length <= 0) {
                    console.error('Order is empty');
                    return;
                }
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    if (order.table) {
                        var table_id = order.table.id
                        var table = this.pos.tables_by_id[table_id]
                        if (!table) {
                            console.error('Order have not table, can not render')
                            continue;
                        }
                        for (var j = 0; j < order.orderlines.models.length; j++) {
                            var line = order.orderlines.models[j];
                            if (line.product.pos_categ_id[0] == undefined) {
                                console.log('category product line underfined');
                                continue;
                            }
                            if (line.state == 'Done') {
                                console.log('state is DONE, pass');
                                continue;
                            }
                            if (line.state == 'Need-to-confirm') {
                                console.log('Need-to-confirm, pass');
                                continue;
                            }
                            if (categs.indexOf(line.product.pos_categ_id[0]) == -1) {
                                console.log('Not the same category product and pos config category');
                                continue;
                            }
                            if (line.quantity_updated && line.quantity_updated < line.quantity) {
                                items.push(line);
                            } else if (!line.quantity_updated) {
                                items.push(line);
                            } else if (line.quantity_updated > line.quantity) {
                                console.log('quantity_updated > quantity of line')
                            }
                        }
                    }
                }
            }
            if (items.length > 0) {
                this.render_items(items);
            }
            this.$('.kitchen_delivery').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var orders = self.pos.get('orders').models;
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    var line = order.orderlines.models.find(function (line) {
                        return line.uid == line_uid;
                    })
                    if (line && line.order) {
                        line.set_state('Waiting-delivery');
                    }
                }
            });
            this.$('.kitchen_cancel').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var orders = self.pos.get('orders').models;
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    for (var j = 0; j < order.orderlines.models.length; j++) {
                        var line = order.orderlines.models[j]
                        if (line.uid == line_uid) {
                            line.set_state('Not-enough-material');
                        }
                    }
                }
            });
            this.$('.kitchen_put_back').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var orders = self.pos.get('orders').models;
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    for (var j = 0; j < order.orderlines.models.length; j++) {
                        var line = order.orderlines.models[j]
                        if (line.uid == line_uid) {
                            line.set_state('Confirmed');
                        }
                    }
                }
            });
            this.$('.kitchen_confirm_cancel').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var orders = self.pos.get('orders').models;
                for (var i = 0; i < orders.length; i++) {
                    var order = orders[i];
                    for (var j = 0; j < order.orderlines.models.length; j++) {
                        var line = order.orderlines.models[j]
                        if (line.uid == line_uid) {
                            line.set_state('Kitchen confirmed cancel');
                        }
                    }
                }
            });
        },
    });
    gui.define_screen({
        'name': 'kitchen_screen',
        'widget': KitchenScreenWidget,
    });
});

