from odoo import fields, models,api

class prepayment_schedule(models.TransientModel):
    _name = "prepayment.schedule"
    _description = "Customer Prepayment Schedule"

    payment_id = fields.Many2one('account.journal', 'Payment Method')
    frequency_method = fields.Selection([('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], string='Frequency Method',track_visibility='onchange')
    frequency = fields.Integer(string='Frequency',default = 1,track_visibility='onchange')
    date= fields.Date('First Date',track_visibility='onchange')
    prepaid_account = fields.Many2one('account.account',string= "Prepaid Account")
    revenue_account = fields.Many2one('account.account',string= "Revenue Account")

    @api.multi
    def action_confirm(self):
        context = dict(self._context)
        invoice_id = context.get('active_id')
        invoice_obj = self.env['account.invoice'].browse(invoice_id)
        invoice_obj.action_invoice_open()
        invoice_obj.write({'state': 'prepaid'})
        vals = {
            'journal_id': self.payment_id.id,
            'frequency_method': self.frequency_method,
            'frequency': self.frequency,
            'date': self.date,
            'prepaid_account': self.prepaid_account.id,
            'revenue_account': self.revenue_account.id,
            'invoice_id': invoice_obj.id,
            'partner_id': invoice_obj.partner_id.id,
            'state': 'inprogress',
        }
        if invoice_obj.type == 'out_invoice':
            prepayment_obj = self.env['customer.prepayment.schedule'].create(vals)
            prepayment_obj.compute()
        elif invoice_obj.type == 'in_invoice':
            prepayment_obj = self.env['supplier.prepayment.schedule'].create(vals)
            prepayment_obj.compute()
        return True

prepayment_schedule()