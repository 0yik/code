# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_inv_number(self):
        for rec in self:
            if rec.number:
                rec.inv_number = rec.number
            if rec.state in ['proforma','proforma2']:
                rec.inv_number = rec.proforma_number
                rec.is_proforma = True

    is_proforma = fields.Boolean(compute='get_inv_number',string='Is Pro-Forma',default=False)
    proforma_number = fields.Char(string='Pro-Forma Number', store=True, readonly=True, copy=False)
    inv_number = fields.Char(string='Inv Number', compute='get_inv_number')

    @api.multi
    def action_invoice_proforma2(self):
        res = super(AccountInvoice, self).action_invoice_proforma2()
        for rec in self:
            rec.write({
                'proforma_number': self.env['ir.sequence'].next_by_code('account.proforma.customer.invoice'),
            })
        return res