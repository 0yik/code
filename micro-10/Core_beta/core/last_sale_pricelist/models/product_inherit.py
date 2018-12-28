from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError



class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    
    price_list_line = fields.One2many('sale.price.list', 'product_id' ,string="Price List Line")
    
    
class SalePriceList(models.Model):
    _name = 'sale.price.list'
    
    product_id = fields.Many2one('product.template', string="Product")
    partner_id = fields.Many2one('res.partner', string="Partner")
    product_variant_id = fields.Many2one('product.product', string="Product Variant") 
    order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_date = fields.Datetime(string="Sale Date")
    price_unit = fields.Float(string="Sale Price")
    product_qty = fields.Float(string="Quantity")
    sales_person_id = fields.Many2one('res.users', string="Sales Person")