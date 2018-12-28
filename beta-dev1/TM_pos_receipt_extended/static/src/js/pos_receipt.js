odoo.define('TM_pos_receipt_extended.TM_pos_receipt_extended', function(require) {
    "use strict";
    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var gui = require('point_of_sale.gui');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var core = require('web.core');
    var PopupWidget = require('point_of_sale.popups');
    var chrome = require('point_of_sale.chrome');
    var module = require('point_of_sale.DB')
    var QWeb = core.qweb;
    var _t = require('web.core')._t;


    models.load_fields('res.company', ['street', 'street2', 'state_id', 'country_id', 'city', 'website']);


    models.load_models({
        model: 'pos.config',
        fields: [],
        domain: function(self) {
            return [
                ['id', '=', self.pos_session.config_id[0]]
            ];
        },
        loaded: function(self, configs) {
            self.config = configs[0];
            self.config.use_proxy = self.config.iface_payment_terminal ||
                self.config.iface_electronic_scale ||
                self.config.iface_print_via_proxy ||
                self.config.iface_scan_via_proxy ||
                self.config.iface_cashdrawer;

            if (self.config.company_id[0] !== self.user.company_id[0]) {
                throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
            }

            self.db.set_uuid(self.config.uuid);
            self.cashier = self.get_cashier();
            self.salesman = self.get_salesman();

            var orders = self.db.get_orders();
            for (var i = 0; i < orders.length; i++) {
                self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number + 1);
            }
        },
    }, {
        'after': 'pos.config'
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            _super_order.initialize.apply(this, arguments);
            if (options.json) {
                this.init_from_JSON(options.json);
            } else {
                this.sequence_number = this.pos.pos_session.sequence_number++;
                this.uid = this.generate_unique_id();
                this.name = _t("CS/TM/") + this.uid;
                this.validation_date = undefined;
                this.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                    return fp.id === self.pos.config.default_fiscal_position_id[0];
                });
            }
            this.salesman = null;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.name = _t("CS/TM/") + this.uid;
        },
        generate_unique_id: function() {
            // Generates a public identification number for the order.
            // The generated number must be unique and sequential. They are made 12 digit long
            // to fit into EAN-13 barcodes, should it be needed 
            var date = new Date();

            function zero_pad(num, size) {
                var s = "" + num;
                while (s.length < size) {
                    s = "0" + s;
                }
                return s;
            }
            return this.pos.config.branch_id[0] + '/' + String(date.getFullYear()) + '' + String(date.getMonth()) + '' + String(zero_pad(this.sequence_number, 5));
        },

    });

    var PosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        initialize: function(attributes, options) {
            PosModel.initialize.apply(this, arguments);
            this.salesman = null;
        },
        get_salesman: function() {
            return this.db.get_salesman() || this.salesman || this.user;
        },
        set_salesman: function(name) {
            this.salesman = name;
            this.db.set_salesman(this.salesman);
        },
    });

    var SalesnameWidget = PosBaseWidget.extend({
        template: 'SalesnameWidget',
        init: function(parent, options) {
            options = options || {};
            this._super(parent, options);
        },
        renderElement: function() {
            var self = this;
            this._super();

            this.$el.click(function() {
                self.click_salesname();
            });
        },
        click_salesname: function() {
            var self = this;
            this.gui.select_user({
                'security': true,
                'current_user': this.pos.get_cashier(),
                'title': _t('Change Sales Person'),
            }).then(function(user) {
                self.pos.set_salesman(user);
                self.renderElement();
            });
        },
        get_name_salesman: function() {
            var user = this.pos.salesman || this.pos.user;
            if (user) {
                return user.name;
            } else {
                return "";
            }
        },
    });


    var chrome_obj = chrome.Chrome.prototype
    chrome_obj.widgets.push({
        'name': 'SalesnameWidget',
        'widget': SalesnameWidget,
        'append': '.pos-branding',
    });

    module.include({
        init: function(options) {
            this._super(options);
            this.salesman = {};
        },
        set_salesman: function(name) {
            // Always update if the user is the same as before
            this.salesman = name
            this.save('salesman', name);
        },
        get_salesman: function() {
            return this.load('salesman');
        }
    });

    var HomeDeliveryWidget = screens.ActionButtonWidget.extend({
        template: 'HomeDeliveryNew',

        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var orderlines = order.orderlines.models;
            if(orderlines.length < 1){
                self.gui.show_popup('error',{
                        'title': _t('Empty Order !'),
                        'body': _t('Please select some products'),
                    });
                return false;
            }
            this.gui.show_popup('delivery_order',{
                'title': _t('Home Delivery Order'),
                'name' : order.get_div_name(),
                'email' : order.get_div_email(),
                'mobile' : order.get_div_mobile(),
                'address' : order.get_div_location(),
                'street' : order.get_div_street(),
                'city' : order.get_div_city(),
                'zip' : order.get_div_zip(),
                'delivery_date' : order.get_delivery_date() ,
                'person_id' : order.get_div_person(),
                'order_note' : order.get_div_note(),
            });
        },
    });

    screens.define_action_button({
        'name': 'home_delivery',
        'widget': HomeDeliveryWidget,
        'condition': function() {
            return true;
        },
    });

});