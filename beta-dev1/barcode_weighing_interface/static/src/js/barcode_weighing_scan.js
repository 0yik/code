odoo.define('barcode_weighing_interface', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var Class = require('web.Class');
    var Model = require('web.Model');
    var session = require('web.session');
    var PlannerCommon = require('web.planner.common');
    var framework = require('web.framework');
    var webclient = require('web.web_client');
    var PlannerDialog = PlannerCommon.PlannerDialog;

    var QWeb = core.qweb;
    var _t = core._t;

    var BarcodeScanner = Class.extend({
        connect: function (callback) {
            var code = "";
            var timeStamp = 0;
            var timeout = null;
            this.handler = function (e) {
                if (e.which === 13) { //ignore returns
                    return;
                }
                if (timeStamp + 50 < new Date().getTime()) {
                    code = "";
                }

                timeStamp = new Date().getTime();
                clearTimeout(timeout);

                code += String.fromCharCode(e.which);

                timeout = setTimeout(function () {
                    if (code.length >= 3) {
                        callback(code);
                    }
                    code = "";
                }, 100);
            };
            $(document).off('keydown');
            $(document).off('keypress');
            // $(document).on('keypress', this.handler);
            // $(window.document).on('keypress', this.handler)
            $(document).on('keydown', this.handler);
        },
        disconnect: function () {
            // $(document).off('keypress', this.handler);
            $(document).off('keydown', this.handler);
        },
    });

    var BarcodeWeighingInterFace = Widget.extend({
        template: 'BarcodeWeighingWidget',
        events: {
            'click .js_barcode_weighing_close': 'button_close',
            'click .js_barcode_weighing_done': 'button_done',
        },
        init: function (parent, data) {
            console.log("Loading Barcode Weighing InterFace");

            this.check_barcode_input = false;
            this.check_weighing_input = false;
            this.barcode_scanner = new BarcodeScanner();

            if (!('active_id' in data.context)) {
                return this._super.apply(this, arguments);
            }
            this.active_id = data.context.active_id;
            this.order_name = data.context.order_name;
            this.data = data.context.data;
            this.load_product_data(this.data[0]);
            this.data.splice(0, 1);
            return this._super.apply(this, arguments);
        },

        start: function () {
            var self = this;
            return self.load_barcode_scan();
        },

        load_barcode_scan: function () {
            var self = this;
            console.log('Loaded barcode scaner');
            this.barcode_scanner.connect(function (ean) {
                self.show_product_detail(ean);
            });
        },

        show_product_detail: function (ean) {
            var self = this;
            return new Model('stock.production.lot').call('search_read', [[['name', '=', ean]], ['product_id', 'life_date']], {})
                .then(function (result) {
                    if (result.length != 0) {
                        self.check_barcode(result, ean);
                    }
                })
        },

        do_show_stock_lot: function (res, ean) {
            var data = {};
            data.product_name = res[0].product_id[1] || '';
            data.lot_number = ean;
            data.life_date = res[0].life_date || '';
            var table_content = QWeb.render('BarcodeWeighingWidgetTableContent', {widget: data});
            $('.b_product_table > tbody').append(table_content);
        },

        check_barcode: function (res, ean) {
            if (res[0].product_id[0] === this.product_id) {
                this.barcode_scanner.disconnect();
                this.do_show_stock_lot(res, ean);
                this.check_barcode_input = true;
            }
            if (this.check_barcode_input) {
                this.enable_done_button();
            }
        },

        enable_done_button: function () {
            $('.js_barcode_weighing_done').prop("disabled", false);
        },

        disable_done_button: function () {
            $('.js_barcode_weighing_done').prop("disabled", true);
        },

        button_close: function () {
            var self = this;
            this.destroy();
            this.barcode_scanner.disconnect();
            return new Model("ir.model.data").get_func("search_read")([['name', '=', 'action_mrp_workorder_workcenter']], ['res_id']).pipe(function (res) {
                window.location = '/web#id=' + self.active_id + '&view_type=form&model=mrp.workorder&action=' + res[0]['res_id'];
            });
        },

        button_done: function () {
            if ($('.js_barcode_weighing_done').html() === 'End') {
                return this.button_close()
            }
            var self = this;
            var current_recipe_line = this.recipe_line_id;
            this.load_product_data(this.data[0]);
            this.reload_interface(this.data[0]);
            this.data.splice(0, 1);
        },

        reload_interface: function (res) {
            if (res) {
                $('.b_material_name').html(res.product_name + ':');
                $('.b_material_qty').html(res.product_qty);
                $('.b_material_uom').html(res.product_uom);
                $('.b_product_table > tbody').html('');

                $('.b_weighing_input').val("");
                $('.b_weighing_input').css("background-color", "white");
                $('.b_weighing_input').attr('placeholder', "Weighing Input " + res.product_uom);

                this.check_barcode_input = false;
                this.disable_done_button();
                this.load_barcode_scan();
            }
            if (res.end) {
                $('.js_barcode_weighing_done').html('End');
            }
        },
        load_product_data: function (res) {
            this.product_name = res.product_name;
            this.product_id = res.product_id;
            this.product_qty = res.product_qty;
            this.product_uom = res.product_uom;
            this.recipe_line_id = res.recipe_line_id;
            this.product_barcode = res.product_barcode;
            if (res.end) {
                this.button_done_html = "End";
            }
            else {
                this.button_done_html = "Done";
            }
        },
    });

    core.action_registry.add('barcode_weighing_widget.main', BarcodeWeighingInterFace);
    return {
        BarcodeWeighingInterFace: BarcodeWeighingInterFace,
    }

});