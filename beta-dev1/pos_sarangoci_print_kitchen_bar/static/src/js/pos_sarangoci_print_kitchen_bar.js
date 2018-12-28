odoo.define('pos_sarangoci_print_kitchen_bar', function (require) {
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');

    var QWeb = core.qweb;

    var KitchenBarScreenWidget = screens.ReceiptScreenWidget.extend({
        template: 'KitchenBarScreenWidget',
        click_next: function(){
            this.gui.show_screen('products');
        },
        click_back: function(){
            this.gui.show_screen('products');
        },
        render_receipt: function(){
            this._super();
            this.$('.receipt-paymentlines').remove();
            this.$('.receipt-change').remove();
        },
        print_web: function(){
            $('.pos-sale-ticket').each(function () {
				if($(this).parent().hasClass('pos')){
					$(this).remove();
				}
            });
			$('.receipt-screen.screen:not(".oe_hidden") .pos-sale-ticket').clone().appendTo(".pos");
			$('.pos').css('height','1000px');
			window.print();
			$('.pos').css('height','100%');
        },
        render_receipt: function() {
            var order = this.pos.get_order();
            this.$('.pos-receipt-container').html(QWeb.render('KitchenView',{
                widget: this, pos: this.pos, order: order, orderlines: order.get_orderlines()
            }));
        },

    });

    models.Order = models.Order.extend({
        template:'Order',
        get_order_lines_qty:function () {

        }
    });

    gui.define_screen({name:'printkitchenbar', widget: KitchenBarScreenWidget});


    var _super_orderline = models.Orderline.prototype;
	models.Orderline = models.Orderline.extend({
		set_order_printed_kitchen: function(order_printed_kitchen){
            this.order_printed_kitchen = order_printed_kitchen;
        },
        get_order_printed_kitchen: function(order_printed_kitchen){
            return this.order_printed_kitchen;
        },
        show_on_print_kitchen: function () {
            return this.state == 'Confirmed' && this.order_printed_kitchen == false;
        },
        get_attribute: function(){
            return this.attribute;
        },
	});

    var ButtonPrintKitchenBar = screens.ActionButtonWidget.extend({
        template: 'ButtonPrintKitchenBar',
        print_xml: function(){
            var order = this.pos.get('selectedOrder');
            if(order.get_orderlines().length > 0){
                var receipt = order.export_for_printing();
                // this.pos.proxy.print_receipt(QWeb.render('KitchenReceipt',{
                //     receipt: receipt, widget: this, pos: this.pos, order: order, orderlines: order.get_orderlines()
                // }));
                var printers = this.pos.printers;
                for(var i = 0; i < printers.length; i++){
                    if ( printers[i].config.name == 'Kitchen'){
                        var receipt = QWeb.render('KitchenReceipt',{
                            widget: this, pos: this.pos, order: order, orderlines: order.get_orderlines()
                        });
                        printers[i].print(receipt);
                    }
                }
            }
        },

        button_click: function(){

            //print
            if (!this.pos.config.iface_print_via_proxy) {
                this.gui.show_screen('printkitchenbar');
            } else {
                this.print_xml();
            }
            // this.gui.show_screen('printkitchenbar');
            //set orderline printed
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            orderlines.forEach(function(orderline){
                if (orderline.state == "Confirmed" && orderline.get_order_printed_kitchen() == false){
                    orderline.set_order_printed_kitchen(true);
                }
            });

            // confirm order
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line && line.state && line.state == 'Need-to-confirm') {
                        line.set_state('Confirmed');
                        line.set_order_printed_kitchen(false);
                    }
                }
            }
            $('.order-submit').click();
        },
    });


    screens.define_action_button({
        'name': 'ButtonPrintKitchenBar',
        'widget': ButtonPrintKitchenBar,
        'condition': function () {
            return this.pos.config.screen_type == 'waiter';
        }
    });
});
