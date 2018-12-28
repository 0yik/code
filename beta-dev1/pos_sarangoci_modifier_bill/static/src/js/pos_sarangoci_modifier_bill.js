odoo.define('pos_sarangoci_modifier_bill', function (require) {
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');

    var QWeb = core.qweb;
    var models = require('point_of_sale.models');
    models.Order = models.Order.extend({
        calculation_order_confirmed: function (){
            var order = this;
            var total_discount = 0;
            var total_price_without_discount = 0;
            var total_price_with_discount = 0;
            var orderlines = this.orderlines;
            orderlines.models.forEach(function (item) {
                if(item.state === 'Confirmed'){
                    if(item.is_complimentary){
                    }else{
                        total_discount += item.discount ? item.price*item.quantity*item.discount / 100 : 0;
                        total_price_without_discount += item.price * item.quantity;
                    }
                }
            });
            total_price_with_discount = total_price_without_discount - total_discount;

            var svm = order.get_service_charge_be();
            if(svm){
                var service_ce = svm.service_charge_computation === 'percentage_of_price' ? ((total_price_with_discount* svm.amount)/100).toFixed(2) : svm.amount;
            }else{
                var service_ce = 0;
            }
            if(!order.service_charge){
                service_ce = 0;
            }
            service_ce = parseFloat(service_ce);
            var tax_use = order.get_tax_charge_be();
            tax_val = 0;
            if(tax_use){
                var tax_val = (tax_use.amount*(total_price_with_discount+service_ce)/100);
            }
            if(!order.tax_charge_value){
                tax_val = 0;
            }
            tax_val = parseFloat(tax_val);
            var total_bef = total_price_with_discount + tax_val + service_ce;
            var rounding = (total_bef % 500);
            var total = total_bef - rounding;
            return {
                'total_discount':total_discount,
                'total_price_without_discount':total_price_without_discount,
                'total_price_with_discount':total_price_with_discount,
                'service_ce':service_ce,
                'tax_val':tax_val,
                'total_bef': total_bef,
                'total' : total,
                'rounding': rounding,
                'tax_amount': tax_use? tax_use.amount + '%': '0%',
                'service_charge_amount':  svm.service_charge_computation === 'percentage_of_price' ? svm.amount + '%' : svm.amount
            }
        }
        // sub total = total price (minus discount if there is discount)
        // service = 2.5% x total price without discount
        // tax = 10% x (total price without discount + service)
        // total = sub total + tax + service
    });

    var NewBillScreenWidget = screens.ReceiptScreenWidget.extend({
        template: 'BillScreenWidget',
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
        should_auto_print: function () {
            return false;
        },
        print_xml: function() {
            var order = this.pos.get('selectedOrder');
            if(order.get_orderlines().length > 0){
                var receipt = order.export_for_printing();
                receipt.bill = true;
                this.pos.proxy.print_receipt(QWeb.render('BillReceipt',{
                    receipt: receipt, widget: this, pos: this.pos, order: order,
                }));
            }
        },
        render_receipt: function() {
            var order = this.pos.get_order();
            this.$('.pos-receipt-container').html(QWeb.render('BillPreview',{
                widget:this,
                order: order,
                receipt: order.export_for_printing(),
                orderlines: order.get_orderlines(),
                paymentlines: order.get_paymentlines(),
            }));
        },
    });

    gui.define_screen({name:'new_bill', widget: NewBillScreenWidget});



    var NewPrintBillButton = screens.ActionButtonWidget.extend({
        template: 'NewPrintBillButton',
        print_xml: function(){
            var order = this.pos.get('selectedOrder');
            if(order.get_orderlines().length > 0){
                var receipt = order.export_for_printing();
                receipt.bill = true;
                this.pos.proxy.print_receipt(QWeb.render('BillReceipt',{
                    receipt: receipt, widget: this, pos: this.pos, order: order,
                }));
            }
        },
        button_click: function(){
            this.gui.show_screen('new_bill');
        },
    });

    screens.define_action_button({
        'name': 'NewPrintBillButton',
        'widget': NewPrintBillButton,
        'condition': function(){
            return this.pos.config.iface_printbill;
        },
    });



    //fix error message['action']
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        syncing_sessions: function (message) {
            if(message){
                var res = _super_posmodel.syncing_sessions.apply(this, arguments);
                return res;
            }
        },
    });

});
