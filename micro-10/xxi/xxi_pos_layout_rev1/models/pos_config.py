from odoo import models,fields,api,_

class pos_config(models.Model):
    _inherit= 'pos.config'

    new_interface = fields.Boolean(string='2 layout Interface')