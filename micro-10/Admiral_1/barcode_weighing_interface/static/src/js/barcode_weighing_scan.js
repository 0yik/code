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
    var workorder_id;
    var product_id;
    var Dialog = require('web.Dialog');
    var BarcodeHandlerMixin = require('barcodes.BarcodeHandlerMixin');

    // var BarcodeScanner = Class.extend({
    //     connect: function (callback) {
    //         var code = "";
    //         var timeStamp = 0;
    //         var timeout = null;
    //         this.handler = function (e) {
    //             if (e.which === 13) { //ignore returns
    //                 return;
    //             }
    //             if (timeStamp + 50 < new Date().getTime()) {
    //                 code = "";
    //             }
    //
    //             timeStamp = new Date().getTime();
    //             clearTimeout(timeout);
    //             code += String.fromCharCode(e.which);
    //
    //             timeout = setTimeout(function () {
    //                 if (code.length >= 3) {
    //                     callback(code);
    //                 }
    //                 code = "";
    //             }, 100);
    //         };
    //         $(document).off('keydown');
    //         $(document).off('keypress');
    //         // $(document).on('keypress', this.handler);
    //         // $(window.document).on('keypress', this.handler)
    //         $(document).on('keydown', this.handler);
    //         // $(document).on('keypress', this.handler);
    //     },
    //     disconnect: function () {
    //         // $(document).off('keypress', this.handler);
    //         $(document).off('keydown', this.handler);
    //     },
    // });

    var BarcodeWeighingInterFace = Widget.extend(BarcodeHandlerMixin, {
        template: 'BarcodeWeighingWidget',
        events: {
            'click .js_barcode_weighing_close': 'button_close',
            'click .js_barcode_weighing_done': 'button_done',
            'click .js_barcode_weighing_pass': 'button_supervisor',
            'change .b_weighing_input': 'onchange_weight',
        },
        init: function (parent, data) {
            console.log("Loading Barcode Weighing InterFace");
            // this._super.apply(this, arguments);
            this.check_barcode_input = false;
            this.check_weighing_input = false;
            BarcodeHandlerMixin.init.apply(this, arguments);
            // this.barcode_scanner = new BarcodeScanner();
            this.lot_number = false;

            if (!('active_id' in data.context)) {
                return this._super.apply(this, arguments);
            }
            this.active_id = data.context.active_id;
            this.order_name = data.context.order_name;
            this.data = data.context.data;
            this.data_detail = data.context.data;
            this.load_product_data(this.data);
            return this._super.apply(this, arguments);
        },

        on_barcode_scanned: function(barcode) {
            var self = this;
            self.show_product_detail(barcode);
        },

        get_weight: function () {
            $.ajax({
                url: "/weighing/scale_read",
                // url: "http://raspberrypi.mshome.net:8069/hw_proxy/scale_read",
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({}),
                success: function (data) {
                    var current_data = $('.b_weighing_input').val();
                    if (parseFloat(current_data) != parseFloat(data.result.weight)) {
                        $('.js_barcode_weighing_done').prop("disabled", true);
                    }
                    $('.b_weighing_input').val(data.result.weight).change();

                },
                error: function (error) {
                    // alert("Connection failed");
                    clearInterval(this.interval);
                }
            });
        },

        onchange_weight: function (e) {
            var weight = $('.b_weighing_input').val();
            new Model("mrp.workorder").call("compare_weight", [this.active_id, this.product_id, weight]).then(function (res) {
                if ((res[0] == true) && ($('.b_material_name').html() != "")) {
                    $('.js_barcode_weighing_done').prop("disabled", false);
                }
                else {
                    $('.js_barcode_weighing_done').prop("disabled", true);
                }
                if ((res[1] == true) && ($('.b_material_name').html() != "")) {
                    $('.js_barcode_weighing_pass').prop("disabled", false);
                }
                else {
                    $('.js_barcode_weighing_pass').prop("disabled", true);
                }
            });
        },

        start: function () {
            var self = this;
            // return self.load_barcode_scan();
        },
        // load_barcode_scan: function () {
        //     var self = this;
        //     console.log('Loaded barcode scaner');
        //     this.barcode_scanner.connect(function (ean) {
        //         self.show_product_detail(ean);
        //     });
        // },
        show_product_detail: function (ean) {
            console.log('show_product_detail', ean);
            var self = this;
            // ean = '8934974151265\,etst2set\,2018\-05\-31';
            var ean_str = ean.split(",");
            if (ean_str.length > 1) {
                ean = ean_str[1].slice(0, -1);
            }
            return new Model('stock.production.lot').call('search_read', [[['name', '=', ean]], ['product_id', 'life_date']], {})
                .then(function (result) {
                    console.log(result, 'result');
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
            $('.b_material_name').html(this.product_name + ':');
            new Model("mrp.workorder").call("get_weight_require", [this.active_id, this.product_id]).then(function (res) {
                $('.b_material_qty').html(res);
            });
            $('.b_material_qty').html(this.product_qty);
            $('.b_material_uom').html(this.product_uom);
            var table_content = QWeb.render('BarcodeWeighingWidgetTableContent', {widget: data});
            $('.b_product_table > tbody').empty();
            $('.b_product_table > tbody').append(table_content);
            $('.js_barcode_weighing_pass').css('display','inline');
        },
        check_barcode: function (res, ean) {
            console.log('check_barcode', res[0].product_id[0], this.product_id);
            for (var i = 0; i < this.data.length; i++) {
                if (this.data[i].product_id == res[0].product_id[0]) {
                    console.log('res', res);
                    this.product_name = res[0].product_id[1];
                    this.product_id = res[0].product_id[0];
                    this.product_uom = this.data[i].product_uom;
                    this.do_show_stock_lot(res, ean);
                    this.interval = setInterval(this.get_weight, 1000);
                    this.check_barcode_input = true;
                    this.lot_number = ean;
                }
            }
        },
        enable_done_button: function () {
            $('.js_barcode_weighing_done').prop("disabled", false);
        },
        disable_done_button: function () {
            $('.js_barcode_weighing_done').prop("disabled", true);
        },
        button_close: function () {
            clearInterval(this.interval);
            var self = this;
            this.destroy();
            // this.barcode_scanner.disconnect();
            return new Model("ir.model.data").get_func("search_read")([['name', '=', 'action_mrp_workorder_workcenter']], ['res_id']).pipe(function (res) {
                window.location = '/web#id=' + self.active_id + '&view_type=form&model=mrp.workorder&action=' + res[0]['res_id'];
            });
        },
        button_done: function () {
            // if ($('.js_barcode_weighing_done').html() === 'End') {
            //     return this.button_close()
            // }
            var self = this;
            var weight = $('.b_weighing_input').val();

            new Model("mrp.workorder").call("update_weight_done", [self.active_id, self.product_id, weight,self.lot_number]).then(function (res) {

            });

            for (var i = 0; i < self.data_detail.length; i++) {
                if (self.data_detail[i].product_id == self.product_id) {
                    self.data_detail[i].quantity_done = weight;
                    self.data_detail[i].lot = self.lot_number;
                }
            }
            this.reload_interface(this.data_detail);
        },
        button_supervisor: function () {
            clearInterval(this.interval);
            var self = this;
            return new Dialog(self, {
                size: 'medium',
                title: _t('To proceed, please enter your password'),
                $content: '<div><label for="password">' + 'Password :' + '</label><input type="password" class="password"/></div>',
                buttons: [{
                    text: _t("Submit"),
                    classes: 'btn-primary',
                    click: function () {
                        var password = $('.password').val();
                        clearInterval(self.interval);
                        new Model("mrp.workorder").call("supervisor_bypass", [password]).then(function (res) {
                            if (res == true) {
                                $('.js_barcode_weighing_done').prop("disabled", false);
                            }
                            else {
                                alert("You have no access to bypass");
                            }
                        });
                    },
                    close: true
                }]
            }).open();
        },

        reload_interface: function (res) {
            $('.b_material_name').html('');
            $('.b_material_qty').html('');
            $('.b_material_uom').html('');
            $('.b_product_table > tbody').html('');
            $('.b_weighing_input').val("");
            $('.b_weighing_input').css("background-color", "white");
            $('.b_weighing_input').attr('placeholder', "Weighing Input ");
            this.disable_done_button();
            this.lot_number = false;
            clearInterval(this.interval);
            $('.js_barcode_weighing_pass').prop("disabled", true);
            if (res) {
                var table_detail = QWeb.render('BarcodeWeighingWidgetTableDetail', {widget: res});
                $('.b_table_detail > tbody').empty();
                $('.b_table_detail > tbody').append(table_detail);
            }
        },
        load_product_data: function (res) {
            // this.product_name = res.product_name;
            // this.product_id = res.product_id;
            // this.product_qty = res.product_qty;
            // this.product_uom = res.product_uom;
            // this.recipe_line_id = res.recipe_line_id;
            // this.product_barcode = res.product_barcode;
            // if (res.end) {
            //     this.button_done_html = "End";
            // }
            // else {
            //     this.button_done_html = "Done";
            // }
            // var table_detail = QWeb.render('BarcodeWeighingWidgetTableDetail', {widget: res});
            this.button_done_html = "Done";
        },
    });

    core.action_registry.add('barcode_weighing_widget.main', BarcodeWeighingInterFace);
    return {
        BarcodeWeighingInterFace: BarcodeWeighingInterFace,
    }
});