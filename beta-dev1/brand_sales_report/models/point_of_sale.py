# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char(string="Name")
    product_brand_ids = fields.One2many('product.lines', 'brand_id', string="Products")
    branch_ids = fields.One2many('branch.lines', 'brand_id', string="Branch")

class ResBranch(models.Model):
    _inherit = 'res.branch'
    
    brand_id = fields.Many2one('product.brand', string="Brand")

    @api.model
    def create(self, vals):
        res = super(ResBranch, self).create(vals)
        if vals.get('brand_id', False):
            line = self.env['branch.lines'].search([('branch_id','=',res.id),('brand_id','=',res.brand_id.id)])
            if not line:
                self.env['branch.lines'].create({'brand_id':res.brand_id.id,'branch_id':res.id})
        return res

    @api.multi
    def write(self, vals):
        brand_id = self.brand_id.id
        res = super(ResBranch, self).write(vals)
        if vals.get('brand_id', False):
            line = self.env['branch.lines'].search([('brand_id','=',vals.get('brand_id', False)),('branch_id','=',self.id)])
            if not line:
                self.env['branch.lines'].with_context({'skip':True}).create({'brand_id':vals.get('brand_id', False),'branch_id':self.id})
            if brand_id != vals.get('brand_id', False):
                line = self.env['branch.lines'].search([('brand_id','=',brand_id),('branch_id','=',self.id)])
                line.with_context({'skip':True}).unlink()
        return res

class ProductLines(models.Model):
    _name = 'product.lines'

    product_id = fields.Many2one('product.product', string="Product")
    brand_id = fields.Many2one('product.brand', string="Brand")

    @api.model
    def create(self, vals):
        res = super(ProductLines, self).create(vals)
        if vals.get('product_id', False):
#             brand_product = self.env['product.lines'].search([('product_id', '=', res.product_id.id), ('id', '!=', res.id)])
#             if brand_product:
#                 brand_product.unlink()

            res.product_id.with_context(from_brand=True).write({'brand_ids': [(4, res.brand_id.id)]})
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductLines, self).write(vals)
        if vals.get('product_id', False):
            self.product_id.brand_ids = [(4, self.brand_id.id)]
        return res

    @api.multi
    def unlink(self):
        for obj in self:
            obj.product_id.with_context(from_brand=True).write({'brand_ids': [(3, obj.brand_id.id)]})
        return super(ProductLines, self).unlink()

class BranchLines(models.Model):
    _name = 'branch.lines'

    brand_id = fields.Many2one('product.brand', string="Brand")
    branch_id = fields.Many2one('res.branch', string="Branch")

    @api.model
    def create(self, vals):
        res = super(BranchLines, self).create(vals)
        if vals.get('branch_id', False) and not self._context.get('skip', False):
            res.branch_id.with_context(from_brand=True).write({'brand_id': res.brand_id.id})
        return res

    @api.multi
    def write(self, vals):
        res = super(BranchLines, self).write(vals)
        if vals.get('branch_id', False):
            self.branch_id = self.brand_id.id
        return res

    @api.multi
    def unlink(self):
        for obj in self:
            if not self._context.get('skip',False):
                obj.branch_id.write({'brand_id':False})
        return super(BranchLines, self).unlink()
        
class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_ids = fields.Many2many("product.brand", 'product_brand_rel', 'product_id', 'brand_id', string="Brand")

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if vals.get('brand_ids', False):
            product = self.env['product.product'].search([('product_tmpl_id', '=', res.id)])
            for brand_id in product.brand_ids:
                brand_product_ids = [x.product_id.id for x in brand_id.product_brand_ids]
                if product.id not in brand_product_ids:
                    brand_id.product_brand_ids = [(0, 0, {'product_id': product.id})]
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if vals.get('brand_ids', False) and not self._context.get('from_brand'):
            product = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
            product_line_ids = self.env['product.lines'].search([('product_id', '=', product.id)])
            brand_ids = [x.brand_id for x in product_line_ids]
            for brand_id in product.brand_ids:
                brand_product_ids = [x.product_id.id for x in brand_id.product_brand_ids]
                if product.id not in brand_product_ids:
                    brand_id.product_brand_ids = [(0, 0, {'product_id': product.id})]
                if brand_id in brand_ids:
                    brand_ids.remove(brand_id)

            for x in brand_ids:
                remove_line_ids = self.env['product.lines'].search([('product_id', '=', product.id), ('brand_id', '=', x.id)])
                remove_line_ids.unlink()
        return res

class ProductProduct(models.Model):
    _inherit = "product.product"

#     brand_id = fields.Many2one('product.brand', string="Brand")
    brand_ids = fields.Many2many("product.brand", 'product_brand_rel', 'product_id', 'brand_id', related='product_tmpl_id.brand_ids', string="Brand")
    branch_ids = fields.Many2many("res.branch", 'product_branch_rel', 'product_id', 'branch_id', string="Branch")

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if vals.get('brand_ids', False):
            for brand_id in res.brand_ids:
                brand_product_ids = [x.product_id.id for x in brand_id.product_brand_ids]
                if res.id not in brand_product_ids:
                    brand_id.product_brand_ids = [(0, 0, {'product_id': res.id})]
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if vals.get('brand_ids', False) and not self._context.get('from_brand'):
#             brand_product = self.env['product.lines'].search([('product_id', '=', self.id)])
#             if brand_product:
#                 brand_product.unlink()
            product_line_ids = self.env['product.lines'].search([('product_id', '=', self.id)])
            brand_ids = [x.brand_id for x in product_line_ids]
            for brand_id in self.brand_ids:
                brand_product_ids = [x.product_id.id for x in brand_id.product_brand_ids]
                if self.id not in brand_product_ids:
                    brand_id.product_brand_ids = [(0, 0, {'product_id': self.id})]
                if brand_id in brand_ids:
                    brand_ids.remove(brand_id)

            for x in brand_ids:
                remove_line_ids = self.env['product.lines'].search([('product_id', '=', self.id), ('brand_id', '=', x.id)])
                remove_line_ids.unlink()
#         if not vals.get('brand_ids', False) and not self._context.get('from_brand'):
#             if brand_product:
#                 brand_product.unlink()
        return res

class pos_config(models.Model):
    _inherit = 'pos.config'

    brand_id = fields.Many2one('product.brand', string="Brand")
# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     brand_ids = fields.Many2many("product.brand", 'user_brand_rel', 'user_id', 'brand_id', string="Brand")
#     screen_type = fields.Selection([
#             ('waiter', 'Waiter'),
#             ('kitchen', 'Kitchen'), ], string='Session Type', default='waiter')
