from odoo import models, fields, api,_

class ProductProduct(models.Model):
    _inherit = "product.template"

    pos_categ_ids = fields.Many2many('pos.category',string="Point of Sale Category")
    
    @api.onchange('pos_categ_ids')
    def onchange_multiple_category(self):
        if self.pos_categ_ids:
            categ = self.pos_categ_ids[0]
            self.pos_categ_id = categ.id