odoo.define('pos_sarangoci_reprint', function (require) {
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        get_date_create_format: function () {
            var dateObj = this.creation_date;
            var month = dateObj.getUTCMonth() + 1; //months from 1-12
            var day = dateObj.getUTCDate();
            var year = dateObj.getUTCFullYear();
            var seconds = dateObj.getSeconds();
            var minutes = dateObj.getMinutes();
            var hour = dateObj.getHours();
            return year + "/" + month + "/" + day +"      "+ hour+":"+minutes+":"+seconds;
        },

    });
    var ReprintButton = screens.ActionButtonWidget.extend({
        template: 'ReprintButton',
        button_click: function() {
            var self = this;
            var user = this.pos.user.id
            var order = this.pos.get_order();
            if(order.get_orderlines().length > 0){
                this.pos.proxy.print_receipt(QWeb.render('RePrintXml',{
                    widget: this, order: order,
                }));
            }


        },
    });

    screens.define_action_button({
        'name': 'ReprintButton',
        'widget': ReprintButton
    });
});
