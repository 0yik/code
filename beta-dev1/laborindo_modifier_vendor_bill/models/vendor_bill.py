from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class vendor_bill(models.Model):
    _inherit = 'account.invoice'

    vendor_bill_no  = fields.Char('Vendor Bill No')
    transaction_no  = fields.Char('Transaction No')
    doc_date        = fields.Date('Doc Completeness Date',default=fields.Date.today())

    # @api.one
    # @api.depends('transaction_no','efaktur_masukan')
    # def _compute_vendor_bill_no(self):
    #     if self.transaction_no and self.efaktur_masukan:
    #         self.vendor_bill_no = self.transaction_no + '.'+ self.efaktur_masukan
    #     else:
    #         self.vendor_bill_no = " "

    @api.onchange('date_invoice')
    def bill_date_onchange(self):
        if self.type == 'in_invoice' and self.date_invoice:
            po_id = self.env.context.get('default_purchase_id', False)
            if po_id:
                purchase_id = self.env['purchase.order'].browse(po_id)
                if purchase_id.payment_term_id:
                    line_id = self.env['account.payment.term.line'].search([('payment_id', '=', purchase_id.payment_term_id.id)], limit=1)
                    if line_id:
                        self.date_due = (datetime.strptime(self.date_invoice,DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=line_id.days)).strftime(DEFAULT_SERVER_DATE_FORMAT)
                    else:
                        self.date_due = self.date_invoice
                else:
                    self.date_due = self.date_invoice
            else:
                self.date_due = self.date_invoice