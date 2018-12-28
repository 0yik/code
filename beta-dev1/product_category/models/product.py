# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    category_main_id = fields.Many2one('category.main', string='Category')
    category_subfirst_id = fields.Many2one('category.subfirst', string='Sub I')
    category_subsecond_id = fields.Many2one('category.subsecond', string='Sub II')

    @api.model
    def create(self,vals):
        res = super(ProductTemplate, self).create(vals)
        if vals.get('category_main_id', False):
            product = self.env['product.product'].search([('product_tmpl_id','=',res.id or False)])
            if product:
                product.write({'category_main_id':vals.get('category_main_id', False) or False})
        if vals.get('category_subfirst_id', False):
            product = self.env['product.product'].search([('product_tmpl_id','=',res.id or False)])
            if product:
                product.write({'category_subfirst_id':vals.get('category_subfirst_id', False) or False})
        if vals.get('category_subsecond_id', False):
            product = self.env['product.product'].search([('product_tmpl_id','=',res.id or False)])
            if product:
                product.write({'category_subsecond_id':vals.get('category_subsecond_id', False) or False})
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if vals.get('category_main_id', False):
            product = self.env['product.product'].search([('product_tmpl_id', '=', self.id or False)])
            if product:
                product.write({'category_main_id': vals.get('category_main_id', False) or False})
        if vals.get('category_subfirst_id', False):
            product = self.env['product.product'].search([('product_tmpl_id', '=', self.id or False)])
            if product:
                product.write({'category_subfirst_id': vals.get('category_subfirst_id', False) or False})
        if vals.get('category_subsecond_id', False):
            product = self.env['product.product'].search([('product_tmpl_id', '=', self.id or False)])
            if product:
                product.write({'category_subsecond_id': vals.get('category_subsecond_id', False) or False})
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    category_main_id = fields.Many2one('category.main', string='Category')
    category_subfirst_id = fields.Many2one('category.subfirst', string='Sub I')
    category_subsecond_id = fields.Many2one('category.subsecond', string='Sub II')

    @api.model
    def create(self,vals):
        if not vals.get('name',False):
            if vals.get('product_tmpl_id',False):
                vals.update({'name':self.env['product.template'].browse(vals.get('product_tmpl_id',False)).name or ''})
        res = super(ProductProduct, self).create(vals)
        return res

class CategoryMain(models.Model):
    _name = 'category.main'

    name = fields.Char(string="Name")

class CategorySubFirst(models.Model):
    _name = 'category.subfirst'

    name = fields.Char(string="Name")
    category_id = fields.Many2one("category.main")
class CategorySubSecond(models.Model):
    _name = 'category.subsecond'

    name = fields.Char(string="Name")
    first_categ_id = fields.Many2one("category.subfirst")

class ProductBrandInherit(models.Model):    
    _inherit = "product.brand"
    
    second_categ_id = fields.Many2one("category.subsecond")
