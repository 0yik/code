from odoo import models, fields, api

class pricelist_item(models.Model):
    _inherit = 'product.pricelist.item'

    @api.multi
    def bulk_verify(self):
        self.unlink()