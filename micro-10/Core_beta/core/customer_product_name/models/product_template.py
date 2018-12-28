# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    
    _inherit = 'product.template'

    customer_ids = fields.One2many('product.customerinfo', 'product_template_id')

class product_product(models.Model):
    
    _inherit = 'product.product'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(product_product, self).name_search(name=name, args=args, operator=operator, limit=limit)
        products = []
        # if name:
        customers = self.env['product.customerinfo'].search([
            ('name', '=', self._context.get('partner_id')),
            '|',
            ('product_code', operator, name),
            ('product_name', operator, name)])
        if customers:
            products = self.search([('product_tmpl_id.customer_ids', 'in', customers.ids)])
        if products:
            for product in products:
                for old_product in res:
                    old_product_rec = self.browse(old_product[0])
                    if old_product_rec.id == product.id:
                        res.remove(old_product)
                customers = self.env['product.customerinfo'].search([
                    ('name', '=', self._context.get('partner_id')),
                    ('product_template_id', '=', product.product_tmpl_id.id),
                ])
                product_name = ''
                if customers.product_code:
                    product_name += '[' + customers.product_code + '] ' 
                else:
                    product_name += '[' + product.default_code + '] '
                 
                if customers.product_name:
                    product_name += customers.product_name 
                else:
                    product_name += product.name
                res.append((product.id, product_name))
        return res

    
class CustomerInfo(models.Model):
    _name = "product.customerinfo"
    _description = "Information about a product customer"
    _order = 'sequence, min_qty desc, price'

    name = fields.Many2one(
        'res.partner', 'Customer',
        domain=[('customer', '=', True)], ondelete='cascade', required=True,
        help="Customer of this product")
    product_name = fields.Char(
        'Customer Product Name',
        help="This customer's product name will be used when printing a request for quotation. Keep empty to use the internal one.")
    product_code = fields.Char(
        'Customer Product Code',
        help="This Customer's product code will be used when printing a request for quotation. Keep empty to use the internal one.")
    sequence = fields.Integer(
        'Sequence', default=1, help="Assigns the priority to the list of product Customer.")
    product_uom = fields.Many2one(
        'product.uom', 'Customer Unit of Measure',
        readonly="1", related='product_template_id.uom_po_id',
        help="This comes from the product form.")
    min_qty = fields.Float(
        'Minimal Quantity', default=0.0, required=True,
        help="The minimal quantity to sale from this customer, expressed in the customer Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    price = fields.Float(
        'Price', default=0.0, digits=dp.get_precision('Product Price'),
        required=True, help="The price to sale a product")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id, index=1)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)
    date_start = fields.Date('Start Date', help="Start date for this vendor price")
    date_end = fields.Date('End Date', help="End date for this vendor price")
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        help="When this field is filled in, the vendor data will only apply to the variant.")
    product_template_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade', oldname='product_id')
    delay = fields.Integer(
        'Delivery Lead Time', default=1, required=True,
        help="Lead time in days between the confirmation of the sale order and the receipt of the products in your warehouse. Used by the scheduler for automatic computation of the sale order planning.")
