# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    ref_no = fields.Char(
        string='Reference No.', size=64, help='Add payment reference')
    tech_zero = fields.Monetary(string='Zero',  help='Technical Field to print zero')

    @api.multi
    def _get_invoice_obj(self):
        self.ensure_one()
        invoice_obj = False
        invoice_obj = self.env['account.invoice'].search(
            [('number', '=', self.communication)], limit=1)
        return invoice_obj

    @api.multi
    def _get_previous_payment(self, partner_id):
        self.ensure_one()
        search_obj = False
        search_obj = self.search([('partner_id', '=', partner_id.id),
                                ('id', '!=', self.id)
                                ], limit=1)
        if search_obj.id < self.id:
            search_obj = search_obj
        else:
            search_obj = False
        return search_obj


AccountPayment()
