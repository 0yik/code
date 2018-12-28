# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class customer_prepayment_schedule(models.Model):
    _name = 'customer.prepayment.schedule'
    _inherit = ['mail.thread']

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            inv = record.invoice_id.number
            partner = record.partner_id.name
            res.append((record['id'], inv + ' - ' + partner))
        return res

    partner_id= fields.Many2one('res.partner', related='invoice_id.partner_id', string='Partner', readonly=True)
    journal_id= fields.Many2one('account.journal', 'Payment Method')
    invoice_id= fields.Many2one('account.invoice', 'Invoice')
    frequency_method= fields.Selection([('weekly', 'Weekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], string='Frequency Method',track_visibility='onchange')
    frequency= fields.Integer(string='Frequency', default=1,track_visibility='onchange')
    lines= fields.One2many('customer.prepayment.schedule.line', 'customer_schedule_id', string="Lines")
    date= fields.Date('First Date',track_visibility='onchange')

    @api.multi
    def compute(self):
        schedule_obj = self.env['customer.prepayment.schedule']
        schedule_line_obj = self.env['customer.prepayment.schedule.line']
        for record in self:
            schedule_search = schedule_obj.search([('invoice_id', '=', record.invoice_id.id)])
            if len(schedule_search) > 1:
                raise ValidationError('Error!\nInvoice : '+ str(record.invoice_id.number or "") + ' Generated')
            for line in record.lines:
                if line.journal_id:
                    raise ValidationError('Error!\nCan not Compute because Journal already generate with Number : ' + str(line.journal_id.name or ""))
            record.lines.unlink()
            first_date = record.date
            prev_date = first_date
            for seq in range(0, record.frequency):
                if record.frequency_method == 'weekly':
                    next_date = (datetime.strptime(prev_date, "%Y-%m-%d") + relativedelta(weeks=int(seq)))
                elif record.frequency_method == 'monthly':
                    next_date = (datetime.strptime(prev_date, "%Y-%m-%d") + relativedelta(months=int(seq)))
                elif record.frequency_method == 'quarterly':
                    next_date = (datetime.strptime(prev_date, "%Y-%m-%d") + relativedelta(months=int(seq * 3)))
                elif record.frequency_method == 'yearly':
                    next_date = (datetime.strptime(prev_date, "%Y-%m-%d") + relativedelta(years=int(seq * 3)))
                else:
                    next_date = False
                vals = {
                    'customer_schedule_id': record.id,
                    'date': next_date,
                    'name': ('Payment %s' % str(seq + 1)),
                    'amount': (record.invoice_id.residual / record.frequency),
                }
                schedule_line_obj.create(vals)
        return True


customer_prepayment_schedule()


class customer_prepayment_schedule_line(models.Model):
    _name = 'customer.prepayment.schedule.line'

    customer_schedule_id= fields.Many2one('customer.prepayment.schedule', 'Customer Schedule')
    date= fields.Date('Date')
    customer_prepayment = fields.Boolean('Customer Prepayment')
    name= fields.Char('Description')
    amount= fields.Float('Amount')
    journal_id = fields.Many2one('account.move','Journal Entry')


    @api.multi
    def do_payment(self):
        for line in self:
            inv = line.customer_schedule_id.invoice_id
            amount = line.amount
            payment_type = inv.type in ('out_invoice', 'in_refund') and 'inbound' or 'outbound'
            if payment_type == 'inbound':
                payment_method = self.env.ref('account.account_payment_method_manual_in')
            else:
                payment_method = self.env.ref('account.account_payment_method_manual_out')
            payment_vals = {}
            payment_vals['payment_date'] = line.date
            payment_vals['payment_type'] = payment_type
            payment_vals['partner_type'] = 'customer'
            payment_vals['payment_method_id'] = payment_method.id
            payment_vals['partner_id'] = inv.partner_id.id
            payment_vals['journal_id'] = line.customer_schedule_id.journal_id.id
            payment_vals['amount'] = abs(amount)
            payment_vals['invoice_ids'] = [(6, 0, inv.ids)]
            payment_vals['customer_prepayment_line_id'] = line.id
            payment_vals['communication'] = inv.type in ('out_invoice', 'in_refund') and inv.reference or inv.number
            payment_id = self.env['account.payment'].create(payment_vals)
            payment_id.post()
            for payment in payment_id.move_line_ids:
                line.write({'journal_id': payment.move_id.id,'customer_prepayment': True})
        return True

    @api.multi
    def customer_prepayment_scheduler(self):
        for record in self.search([('date','=',str(datetime.now())[:10])]):
            record.do_payment()
        return True


customer_prepayment_schedule_line()


class account_payment(models.Model):
    _inherit = 'account.payment'

    customer_prepayment_line_id= fields.Many2one('customer.prepayment.schedule.line', 'Customer Prepayment Line')

account_payment()