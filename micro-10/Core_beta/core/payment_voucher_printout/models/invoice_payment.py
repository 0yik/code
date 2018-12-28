# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    cheque_no = fields.Char('Cheque No')
    checked_by = fields.Char('Checked By')
    approved_by = fields.Char('Approved By')

