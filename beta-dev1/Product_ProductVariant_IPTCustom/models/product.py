from odoo import api, fields, models

class ProductFamily(models.Model):
    _name = 'product.family'
    name = fields.Char('Name', size=256)    

class ProductType(models.Model):
    _name = 'product.type'    
    name = fields.Char('Name', size=256)
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    family_id = fields.Many2one('product.family', 'Product Family')
    fproduct_id = fields.Many2one('product.template', 'Product Family')
    is_template = fields.Boolean('Is Template')
    
    # @api.model
    # def create(self, vals):
        # result = super(ProductProduct, self).create(vals)
        # context = self._context or {}
        # if vals.has_key('family_id'):
            # tmp_id = self.env['product.template'].search([('name','=',self.env['product.family'].browse(vals['family_id']).name)])
            # if not tmp_id:
                # tmp_id = self.env['product.template'].create({'name': self.env['product.family'].browse(vals['family_id']).name})
                # self.env.cr.execute(''' INSERT INTO template_variant_rel values(%s,%s) '''%(str(tmp_id.id),result.id))
            # else:
                # self.env.cr.execute(''' INSERT INTO template_variant_rel values(%s,%s) '''%(str(tmp_id.id),result.id))
        # return result
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    family_id = fields.Many2one('product.family', 'Product Family')
    type_id   = fields.Many2one('product.type', 'Product Type')
    fproduct_ids = fields.Many2many('product.product', 'template_variant_rel', 'template_id', 'product_id', 'Family Product List')
    productf_id = fields.One2many('product.product', 'fproduct_id', 'Family Product List')
    is_variant = fields.Boolean('Is Variant')
    is_template = fields.Boolean('Is Template')