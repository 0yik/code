# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class InvoiceCreditNoteWizard(models.TransientModel):
    """Refunds invoice"""

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
        for form in self:
            for inv in inv_obj.browse(context.get('active_ids')):
                inv_br = inv_obj.browse(inv.id)
                updates = {
                    'number': '',
                    'reason': form.description and form.description or '',
                    'credit_note': True,
                    'invoice_date': form.date_invoice,
                    'date_invoice': form.date,
                    'ref_no': inv.id
                }
                vals = inv_br.copy_data(default=updates)
                invoice_id = inv.create(vals[0])
                imd = self.env['ir.model.data']
                action = self.env.ref('credit_debit_note.action_in_refund_tree1_view1_credit_note').id
                view_id = imd.xmlid_to_res_id('credit_debit_note.supplier_form_inherit')
                result = {
                    'name':'Credit Note',
                    'view_type':'form',
                    'view_mode':'form',
                    'res_model':'account.invoice',
                    'view_id': view_id,
                    'type':'ir.actions.act_window',
                    'res_id':invoice_id.id,
                    'target':'current',
                }
                return result
            return True

