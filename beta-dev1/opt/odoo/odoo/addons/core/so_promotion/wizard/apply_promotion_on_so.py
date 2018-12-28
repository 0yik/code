from odoo import api, fields, models, _


class apply_promotion_on_so(models.TransientModel):
    
    _name = "apply.sale.promotion"
    
    
    @api.model
    def _filter_promotion(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            sale = self.env['sale.order'].browse(active_id)
            filter_ids = []
            for rec in self.env['sale.promotion'].search([]):
                if rec.type == '1_discount_total_order':
                    for discount_order_line in rec.discount_order_ids:
                        if sale.amount_untaxed >= discount_order_line.minimum_amount: 
                            filter_ids.append(rec.id)
                            continue
                elif rec.type ==  '2_discount_category':
                    for order_line in sale.order_line:
                        if order_line.product_id.categ_id:
                            categories_ids = [order_line.product_id.categ_id.id]
                            def append_categories_ids(category):
                                if category.parent_id:
                                    categories_ids.append(category.parent_id.id)
                                    append_categories_ids(category.parent_id)
                            append_categories_ids(order_line.product_id.categ_id)
                            for discount_category_id in rec.discount_category_ids:
                                if discount_category_id.category_id.id in categories_ids: 
                                    filter_ids.append(rec.id)
                                    continue
                elif rec.type ==  '3_discount_by_quantity_of_product':
                    for order_line in sale.order_line:
                        for discount_quantity_id in rec.discount_quantity_ids:
                            if discount_quantity_id.product_id.id == order_line.product_id.id and order_line.product_uom_qty >= discount_quantity_id.quantity:  
                                filter_ids.append(rec.id)
                                continue
                elif rec.type ==  '4_pack_discount':
                    
                    domain = []
                    
                    
                    
#                     sale_order_products = []
#                     for order_line in sale.order_line:
#                         sale_order_products.append(order_line.product_id.id)
#                     
#                     pack_product_ids = []
#                     for discount_condition_id in rec.discount_condition_ids:
#                         pack_product_ids.append(discount_condition_id.product_id.id)
#                             
#                     if all(elem in sale_order_products  for elem in pack_product_ids):
#                         
#                     else:
#                         continue
                    
#                 elif rec.type ==  '5_pack_free_gift':
#                     print '55555555555555555'
#                 elif rec.type ==  '6_price_filter_quantity':
#                     print '66666666666666666'
            return [('id', 'in', filter_ids)]
        return []
    
    
    sale_promotion_ids = fields.Many2many('sale.promotion', string='Discounts', domain=_filter_promotion)
    
    
    
    