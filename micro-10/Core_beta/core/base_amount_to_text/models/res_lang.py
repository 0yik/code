from odoo import fields, models

class ResLang(models.Model):
    _inherit = 'res.lang'

    amount_to_text_ids = fields.One2many(
        comodel_name='base.amount_to_text',
        inverse_name='lang_id',
        string='Amount To Text'
    )
