from odoo import api, fields, models

class account_payments(models.Model):
    _inherit = 'account.payment'

    cheque_number = fields.Char(string='Cheque Number')