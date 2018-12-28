odoo.define('max_amount_for_promotion', function (require) {

    var models = require('point_of_sale.models');
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
		compute_discount_total_order: function (promotion) {
            var discount_line_tmp = this.checking_apply_total_order(promotion)
            var total_order = this.get_total_without_promotion_and_tax();
            var final_amount = 0.00
            if (total_order > discount_line_tmp.maximum_amount){
            	final_amount = discount_line_tmp.maximum_amount;
            }else{
            	final_amount = total_order 
            }
            if (discount_line_tmp) {
                var product = this.pos.db.get_product_by_id(promotion.product_id[0]);
                if (product) {
                    this.add_product(product, {
                        price: -final_amount / 100 * discount_line_tmp.discount
                    })
                    var selected_line = this.get_selected_orderline();
                    selected_line.promotion_discount_total_order = true;
                    selected_line.promotion = true;
                    selected_line.promotion_reason = 'discount ' + discount_line_tmp.discount + ' % ' + ' when total order greater or equal ' + discount_line_tmp.minimum_amount;
                    selected_line.trigger('change', selected_line);
                }
            }
        },
    })  
})