from odoo import models,fields, api

class sale_order(models.Model):
    _inherit = 'stock.warehouse'


    partner_text = fields.Text('Address')