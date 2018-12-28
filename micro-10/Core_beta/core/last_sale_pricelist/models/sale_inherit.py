from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError



class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        self.order_line = False
        return res
    
    @api.multi
    def action_done(self):
        res = super(SaleOrder, self).action_done()
        for line in self.order_line:
            price_list_id = self.env['sale.price.list'].search([('product_id', '=', line.product_id.product_tmpl_id.id),('product_variant_id', '=', line.product_id.id),('partner_id', '=', line.order_id.partner_id.id)],limit=1)
            
            if price_list_id:
                
                price_vals = {
                                #'partner_id' : self.partner_id.id,
                                'product_variant_id' : line.product_id.id,
                                'order_id' : self.id,
                                'sale_date' : self.confirmation_date,
                                'price_unit' : line.price_unit,
                                'product_qty' : line.product_uom_qty,
                                'sales_person_id': self.user_id.id,
                            }
                price_list_id.write(price_vals)
                
            else:
                price_vals = {  'product_id' : line.product_id.product_tmpl_id.id,
                                'product_variant_id': line.product_id.id,
                                'partner_id' : self.partner_id.id,
                                'order_id' : self.id,
                                'sale_date' : self.confirmation_date,
                                'price_unit' : line.price_unit,
                                'product_qty' : line.product_uom_qty,
                                'sales_person_id': self.user_id.id,
                            }
                self.env['sale.price.list'].create(price_vals)
        return res    
    
    
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleOrderLine, self).product_uom_change()
        if not self.order_id.partner_id:
            raise UserError("Please select customer first.")
        price_list_id = self.env['sale.price.list'].search([('product_id', '=', self.product_id.product_tmpl_id.id),('product_variant_id', '=', self.product_id.id),('partner_id', '=', self.order_id.partner_id.id)],limit=1)
        if price_list_id:
            self.price_unit = price_list_id.price_unit
        return res
        
        
        
        