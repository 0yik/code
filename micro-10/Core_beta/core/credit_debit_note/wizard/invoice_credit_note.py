# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class InvoiceCreditNoteWizard(models.TransientModel):
    _name = "invoice.credit.note.wizard"
    _description = "Invoice Credit Note"

    @api.model
    def default_get(self, fields):
        result = super(InvoiceCreditNoteWizard, self).default_get(fields)
        if self._context.get('active_id'):
            invoice_detatils = self.env['account.invoice'].browse(self._context.get('active_id'))
            result['date_invoice'] = invoice_detatils.date_invoice
        return result

    date_invoice = fields.Date(string='Invoice Date', required=True)
    date = fields.Date(string='Accounting Date')
    description = fields.Char(string='Reason', required=True)

    @api.multi
    def compute_credit_note(self):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        invoice = inv_obj.browse(context.get('active_id'))
        data = {
            'number': '',
            'reason': self.description or '',
            'credit_note': True,
            'invoice_date': self.date_invoice,
            'date_invoice': self.date,
            'ref_no': invoice.id,
            'type': 'out_refund'
        }
        vals = invoice.copy_data(default=data)
        new_invoice = inv_obj.create(vals[0])
        view_id = self.env['ir.model.data'].xmlid_to_res_id('credit_debit_note.supplier_form_inherit')
        result = {
            'name': 'Credit Note',
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': new_invoice.id,
            'target': 'current',
        }
        return result

InvoiceCreditNoteWizard()