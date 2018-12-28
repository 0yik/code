# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FabricFabric(models.Model):
    _name = 'fabric.fabric'
    
    def _get_default_uom_id(self):
        return self.env["product.uom"].search([], limit=1, order='id').id
    
    name = fields.Char("Fabric ID", required=True)
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=True)
    description = fields.Char("Description")
    
class ResCompany(models.Model):
    _inherit = 'res.company'
    
    report_header = fields.Binary("Report Header")