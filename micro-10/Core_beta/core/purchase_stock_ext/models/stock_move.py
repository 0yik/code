# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class StockMoveSupplierInfo(models.Model):
    _name = "stock.move.supplierinfo"
    _description = "Information about a product vendor"
    _order = 'id desc'

    name = fields.Many2one(
        'res.partner', 'Vendor',
        domain=[('supplier', '=', True)], ondelete='cascade', required=True,
        help="Vendor of this product")
    product_name = fields.Char(
        'Vendor Product Name',
        help="This vendor's product name will be used when printing a request for quotation. Keep empty to use the internal one.")
    barcode_ref = fields.Char(
        'Barcode')
    product_code = fields.Char(
        'Vendor Product Code',
        help="This vendor's product code will be used when printing a request for quotation. Keep empty to use the internal one.")
    sequence = fields.Integer(
        'Sequence', default=1, help="Assigns the priority to the list of product vendor.")
    product_uom = fields.Many2one(
        'product.uom', 'Vendor Unit of Measure',
        readonly="1", related='product_tmpl_id.uom_po_id',
        help="This comes from the product form.")
    min_qty = fields.Float(
        'Minimal Quantity', default=0.0, required=True,
        help="The minimal quantity to purchase from this vendor, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    price = fields.Float(
        'Price', default=0.0, digits=dp.get_precision('Product Price'),
        required=True, help="The price to purchase a product")
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
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True, ondelete='cascade', oldname='product_id')
    delay = fields.Integer(
        'Delivery Lead Time', default=1, required=True,
        help="Lead time in days between the confirmation of the purchase order and the receipt of the products in your warehouse. Used by the scheduler for automatic computation of the purchase order planning.")
    stock_move_ref_id = fields.Many2one('stock.move', "Stock Move ref")

StockMoveSupplierInfo()



class StockMove(models.Model):
    _inherit = 'stock.move'

    stockmove_seller_ids = fields.One2many('stock.move.supplierinfo', 'stock_move_ref_id', 'Vendors')

StockMove()