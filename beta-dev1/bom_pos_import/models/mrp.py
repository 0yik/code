from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    included_bom = fields.Boolean('Included in Bom')

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(MrpBom, self).onchange_product_tmpl_id()
        if self.product_tmpl_id:
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
            if product_id:
                self.product_id = product_id.id
        return res
