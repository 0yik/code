odoo.define('pos_bus_restaurant_screen', function (require) {
    var gui = require('point_of_sale.gui');
    var floor = require('pos_restaurant.floors');
    var pos_bus_screen = require('pos_bus_screen');
    var splitbill = require('pos_restaurant.splitbill')

    var FloorScreenWidget;
    var SplitbillScreenWidget;
    _.each(gui.Gui.prototype.screen_classes, function (o) {
        if (o.name == 'floors') {
            FloorScreenWidget = o.widget;
            FloorScreenWidget.include({
                start: function () {
                    var self = this;
                    this._super();
                    this.pos.bind('update:floor-screen', function () {
                        self.renderElement();
                    })
                },
            })
        }
        if (o.name == 'splitbill') {
            SplitbillScreenWidget = o.widget;
            SplitbillScreenWidget.include({
                pay: function (order, neworder, splitlines) {
                    var res = this._super(order, neworder, splitlines);
                    return res;
                }
            })
        }
    });
})
