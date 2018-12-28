# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mgm_modifer_tax_adjustment(models.TransientModel):
    _inherit = 'tax.adjustments.wizard'

    invoice_id = fields.Many2one('account.invoice', string="Invoice",domain=[('type', 'in', ['out_invoice','in_invoice']), ('debit_note', '=', False), ('credit_note', '=', False)])

class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def name_get(self):
        if 'select_from_tax_adjustment' in self._context:
            result = []
            for record in self:
                name = record.number
                if record.type == 'out_invoice' and not record.debit_note:
                    name = "Customer Invoice %s" % (name or '')
                if record.type == 'in_invoice' and not record.credit_note:
                    name = "Vendor Bill %s" % (name or '')
                result.append((record.id, name))
            return result
        else:
            return super(account_invoice, self).name_get()
