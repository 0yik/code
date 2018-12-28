odoo.define('tm_pos_print_home_delivery.tm_pos_print_home_delivery', function (require) {
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var PosDB = require("point_of_sale.DB");
    var _super_posmodel = models.PosModel.prototype;
    var QWeb = core.qweb;
    var ActionManager1 = require('web.ActionManager');
    var Model = require('web.DataModel');
    var _t = core._t;


    var _super_order_line = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function () {
            var json = _super_order_line.export_as_JSON.apply(this, arguments);
            json.product_currency_symbol = this.pos.currency.symbol;
            json.product_name = this.product.name;
            json.product_uom_name = this.product.uom_id[1];
            return json;
        },
    });

    for (var index in gui.Gui.prototype.popup_classes) {
        if(gui.Gui.prototype.popup_classes[index].name=='delivery_order'){
            var popup =  gui.Gui.prototype.popup_classes[index].widget;
            popup.include({
                events: _.extend({}, popup.prototype.events, {
                    'click .button.print': 'click_print',
                }),
                click_print: function () {
                    var self = this;
                    var fields = {};
                    this.$('.detail').each(function(idx, el){
                        fields[el.name] = el.value || false;
                    });
                    var report = new Model('pos.order.delivery.report');
                    report.call('get_id_action_report', [false, fields,self.pos.get_order().export_as_JSON(),])
                    .then(function(result) {
                        this.action_manager = new ActionManager1(this);
                        this.action_manager.do_action(result[0], {
                            additional_context: {
                                active_id: result[1],
                                active_ids: [result[1]],
                                active_model: 'pos.order.delivery.report'
                            }
                        });
                        self.gui.show_screen('products');
                    })
                    .fail(function(error, event) {
                        self.gui.show_popup('error', {
                            'title': _t("Error!!!"),
                            'body': _t("Check your internet connection and try again."),
                        });
                    });
                }
            })
        }
    }
});
