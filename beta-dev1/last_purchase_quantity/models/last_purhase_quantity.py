from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    last_qty = fields.Char(string='Last Qty')
    last_date = fields.Char(string='Last Date')
    # brand = fields.Many2one('product.brand',string='Brand')

    # @api.onchange('brand')
    # def product_list_brand(self):
    #     if self.brand:
    #         return {'domain':{'product_id':[('product_brand_id','=',self.brand.id)]}}
    #     else:
    #         return {'domain': {'product_id': []}}
    @api.onchange('product_id')
    def onchange_product_id(self):
        purchase_order_line = self.env['purchase.order.line'].search([('product_id','=',self.product_id.id),('state','=','purchase')],order='id desc',limit=1)
        self.last_qty = purchase_order_line.product_qty
        self.last_date = purchase_order_line.date_order
        product_template_record = self.env['product.template'].search([('name','=',self.product_id.name)])
        # self.brand = product_template_record.product_brand_id

        return super(PurchaseOrderLine, self).onchange_product_id()	

