from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_available_credit(self):
        for record in self:
            if record.credit_limit - record.credit > 0 and record.credit >= 0:
                record.available_credit = record.credit_limit - record.credit
            elif record.credit < 0:
                record.available_credit = record.credit_limit
            else:
                record.available_credit = 0.0

    available_credit = fields.Float(compute='get_available_credit', string='Available Credit')

ResPartner()