// pos_coupons_gift_voucher js
//console.log("custom callleddddddddddddddddddddd")
odoo.define('pos_coupons_gift_voucher.pos', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var Model = require('web.DataModel');

    var _t = core._t;



    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            //var partner_model = _.find(this.models, function(model){ return model.model === 'pos.gift.coupon'; });
            //partner_model.fields.push('gift_coupen_code');
            //console.log("partner loadedddddddddddddddddddddddddddddddddddd",partner_model);


            var journal_model = _.find(this.models, function(model) {
                return model.model === 'pos.order';
            });
            //journal_model.fields.push('coupon_id');
            //console.log("journal loadedddddddddddddddddddddddddddddddddddd", journal_model);
            return _super_posmodel.initialize.call(this, session, attributes);
        },


        push_order: function(order, opts) {
            var self = this;
            //console.log("orderrrrrrrrrrrrrrrrrrr", order)
            var pushed = _super_posmodel.push_order.call(this, order, opts);
            var partner_id = order && order.get_client();;
            //console.log("parterrrrrrrrrrrrrrrrrrr", partner_id);

            var currentOrder = this.get_order();
            //console.log("currentOrdertrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", currentOrder)

            var entered_code = $("#existing_coupon_code").val();
            //console.log("1111111111111111entered_code", entered_code);

            if (entered_code) {
                //var orders = order.pos.pos_order;
                //var order_id = order.uid;
                //console.log("order.pos.pos_orderrrrrrrrrrrrrrrrrrrrrrrr", orders['id'], order_id)
                //console.log("*********************8order.pos.pos_orderrrrrrrrrrrrrrrrrrrrrrrr", order.pos.pos_gift_coupon[0].id)
                //console.log("*********************I())))))))))))))))))))000", order.pos.pos_order[0].coupon_id)

                new Model('pos.gift.coupon').call('search_coupon', [partner_id ? partner_id.id : 0, entered_code]).fail(function(unused, event) {
                    //console.log("search_coupon callledddddddddddddddddddd")
                }).done(function(output) {
                    //console.log("1111111111111111111111111outputttttttttttttttttttttt", output)
                    var model1 = new Model('pos.order');
                    model1.call('write', [currentOrder['sequence_number'], {
                        'coupon_id': output[0]
                    }]).then(null);
                });
            }
            return pushed;
        }
    });




    models.load_models({
        model: 'pos.gift.coupon',
        fields: ['name', 'gift_coupen_code', 'user_id', 'issue_date', 'expiry_date', 'validity', 'total_available', 'partner_id', 'order_ids', 'active', 'amount', 'description'],
        domain: null,
        loaded: function(self, pos_gift_coupon) {
            //console.log("111111111111loadedddddddddddddddddddddddddddddddddddd",models);
            self.pos_gift_coupon = pos_gift_coupon;
            //console.log("***************self.pos_gift_coupondddddddddddddddddddd", self.pos_gift_coupon);
        },
    });

    models.load_models({
        model: 'pos.order',
        fields: ['coupon_id'],
        domain: null,
        loaded: function(self, pos_order) {
            //console.log("111111111111loadedddddddddddddddddddddddddddddddddddd",models);
            self.pos_order = pos_order;
            //console.log("***************self.pos_orderrrrrrrrrrrrrrrr", self.pos_order);
        },
    });


    models.load_models({
        model: 'pos.coupons.setting',
        fields: ['name', 'product_id', 'min_coupan_value', 'max_coupan_value', 'max_exp_date', 'one_time_use', 'partially_use', 'default_name', 'default_validity', 'default_value', 'default_availability', 'active'],
        domain: null,
        loaded: function(self, pos_coupons_setting) {
            //console.log("111111111111loadedddddddddddddddddddddddddddddddddddd",models);
            self.pos_coupons_setting = pos_coupons_setting;
            //console.log("################self.pos_coupons_settinggggggggggggggggggggg",self.pos_coupons_setting);
        },
    });




    // Popup start

    var SelectExistingPopupWidget = popups.extend({
        template: 'SelectExistingPopupWidget',
        init: function(parent, args) {
            this._super(parent, args);
            this.options = {};
        },
        //
        show: function(options) {
            var self = this;
            this._super(options);

        },
        //
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get_order();
            //console.log("selewcted orderrrrrrrrrrrrrr",order)
            //var order2 = order.get_client();
            //console.log("order.get_clienttttttttttttttttttt",order2)
            var selectedOrder = self.pos.get('selectedOrder');
            //console.log("selectedOrderrrrrrrrrrrrrrrrrrrrrrrrrr",selectedOrder)



            this.$('#apply_coupon_code').click(function() {
                //console.log("create-new-couponnnnnnnnnnnnn callleddddddddddddd")
                var entered_code = $("#existing_coupon_code").val();
                //console.log("##################entered_code", entered_code);
                var partner_id = false
                if (order.get_client() != null)
                    partner_id = order.get_client();
                //console.log("parterrrrrrrrrrrrrrrrrrr", partner_id);

                (new Model('pos.gift.coupon')).call('existing_coupon', [partner_id ? partner_id.id : 0, entered_code]).fail(function(unused, event) {
                    //alert('Connection Error. Try again later !!!!');
                }).done(function(output) {

                    //console.log("outputttttttttttttttttttttt", output, partner_id)

                    var orderlines = order.orderlines;
                    //console.log("#######################orderlines", orderlines)
                    //console.log("**************************", entered_code)



                    // Popup Occurs when no Customer is selected...
                    if (!partner_id) {
                        self.gui.show_popup('error', {
                            'title': _t('Unknown customer'),
                            'body': _t('You cannot use Coupons/Gift Voucher. Select customer first.'),
                        });
                        return;
                    }

                    // Popup Occurs when not a single product in orderline...
                    if (orderlines.length === 0) {
                        self.gui.show_popup('error', {
                            'title': _t('Empty Order'),
                            'body': _t('There must be at least one product in your order before it can be apply for voucher code.'),
                        });
                        return;
                    }

                    // Goes inside when atleast product in orderline... 	
                    if (orderlines.models.length) {
                        // Condition True when Entered Code & Backend Coupon code will be same...                	
                        if (output == 'true') {
                            var selectedOrder = self.pos.get('selectedOrder');
                            //console.log("ifffffffffffffff selectedOrderrrrrrrrrrrrrrrrrrrrrrrrrr", selectedOrder)
                            selectedOrder.coupon_id = entered_code;
                            //console.log("coupon_iddddddddddddddddddddddddd", selectedOrder.coupon_id)
                            var total_amount = selectedOrder.get_total_without_tax();
                            //console.log("totallllllllllllllllllllllllllllllllllllll", total_amount)

                            // Read Method to find appllied coupon's amount
                            new Model('pos.gift.coupon').call('search_coupon', [partner_id ? partner_id.id : 0, entered_code]).fail(function(unused, event) {
                                //console.log("search_coupon callledddddddddddddddddddd")
                            }).done(function(output) {
                                //console.log("1111111111111111111111111outputttttttttttttttttttttt", output)
                                var amount = output[1];
                                //console.log("amounttttttttttttttttt_iddddddddddddddddddddddddd", amount)
                                var total_val = total_amount - amount;
                                //console.log("tttttttttttttttttttttttttttttotal", total_val)
                                var product_id = self.pos.pos_coupons_setting[0].product_id[0];
                                //console.log("productttttttttt_iddddddddddddddddddddddddd", product_id)


                                var product = self.pos.db.get_product_by_id(product_id);
                                //console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@product", product)
                                var selectedOrder = self.pos.get('selectedOrder');

                                selectedOrder.add_product(product, {
                                    price: -amount
                                });

                            });


                            self.gui.show_screen('products');
                        } else { //Invalid Coupon Code
                            self.gui.show_popup('error', {
                                'title': _t('Invalid Code !!!'),
                                'body': _t("Voucher Code Entered by you is Invalid. Enter Valid Code..."),
                            });
                        }




                    } else { // Popup Shows, you can't use more than one Voucher Code in single order.
                        self.gui.show_popup('error', {
                            'title': _t('Already Used !!!'),
                            'body': _t("You have already use this Coupon code, at a time you can use one coupon in a Single Order"),
                        });
                    }


                });
            });


        },

    });
    gui.define_popup({
        name: 'select_existing_popup_widget',
        widget: SelectExistingPopupWidget
    });

    // End Popup start


    var GiftButtonWidget = screens.ActionButtonWidget.extend({
        template: 'GiftButtonWidget',
        button_click: function() {
            var order = this.pos.get_order();
            //console.log("orderrrrrrrrrrrrrr",order)
            var self = this;
            this.gui.show_popup('select_existing_popup_widget', {});
        },
    });

    screens.define_action_button({
        'name': 'POS Coupens Gift Voucher',
        'widget': GiftButtonWidget,
        'condition': function() {
            return true;
        },
    });
    // End GiftPopupWidget start	


});
