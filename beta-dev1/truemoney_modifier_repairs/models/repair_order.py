from odoo import models, fields, api

class mrp_repair(models.Model):
    _inherit = 'mrp.repair'

    user_id     = fields.Many2one('res.users','Sales Person',required=True)