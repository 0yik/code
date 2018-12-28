from odoo import models, fields, api

class vit_efaktur(models.Model):

    _inherit = 'vit.efaktur'
    is_reserved = fields.Boolean('Is Reserved')






