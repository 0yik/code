# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class InvoiceDebitNoteWizard(models.TransientModel):
    _name = "invoice.debit.note.wizard"
    _description = "Invoice Debit Note"

    @api.model
    def default_get(self, fields):
        result = super(InvoiceDebitNoteWizard, self).default_get(fields)
        if self._context.get('active_id'):
            invoice_detatils = self.env['account.invoice'].browse(self._context.get('active_id'))
            result['date_invoice'] = invoice_detatils.date_invoice
        return result

    date_invoice = fields.Date(string='Invoice Date', required=True)
    date = fields.Date(string='Accounting Date')
    description = fields.Char(string='Reason', required=True)

    @api.multi
    def compute_debit_note(self):
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        invoice = inv_obj.browse(context.get('active_id'))
        data = {
            'number': '',
            'reason': self.description or '',
            'debit_note': True,
            'invoice_date': self.date_invoice,
            'date_invoice': self.date,
            'ref_no': invoice.id,
            'type': 'in_refund',
        }
        vals = invoice.copy_data(default=data)
        new_invoice = inv_obj.create(vals[0])
        view_id = self.env['ir.model.data'].xmlid_to_res_id('credit_debit_note.invoice_form_debit_note')
        result = {
            'name': 'Debit Note',
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': new_invoice.id,
            'target': 'current',
        }
        return result

InvoiceDebitNoteWizard()