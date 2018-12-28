from odoo import models, fields, api

class stock_move(models.Model):
    _inherit ='stock.move'

    brand       = fields.Many2one('product.brand.list','Brand')
    category    = fields.Many2one('product.category.list','Category')
    sub_category= fields.Many2one('product.sub.category.list','Sub-Category')

    @api.model
    def create(self,vals):
        if vals.get('product_id',False):
            if not vals.get('brand',False):
                vals.update({'brand' : self.env['product.product'].browse(vals.get('product_id',False)).brand.id or False})
            if not vals.get('category',False):
                vals.update({'category' : self.env['product.product'].browse(vals.get('product_id',False)).category.id or False})
            if not vals.get('sub_category',False):
                vals.update({'sub_category' : self.env['product.product'].browse(vals.get('product_id',False)).sub_category.id or False})
        res = super(stock_move, self).create(vals)
        return res
