# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError
now = datetime.datetime.now()

class payment_installment_type(models.Model):
    _name = 'payment.installment.type'

    name = fields.Char('Payment Installment',required=True)
    no_of_installment = fields.Integer('Number of Installment')
    duration = fields.Integer('Duration')
    days_to_pay = fields.Integer('Day(s) to Pay')
    # week_of_issue = fields.Selection([('one', 'One Week'), ('two', 'Two Weeks'), ('three', 'Three Weeks')], 'Week(s) of Issue')

    @api.one
    @api.constrains('duration', 'no_of_installment', 'days_to_pay')
    def validation_durations_digit(self):
        if self.no_of_installment <= 0:
            raise ValidationError(_('Warning! \n Number of Installment must be a value.'))
        if self.duration <= 0:
            raise ValidationError(_('Warning! \n Duration must be a value.'))
        if self.days_to_pay <= 0:
            raise ValidationError(_('Warning! \n Day(s) to Pay must be a value.'))

    # @api.model
    # def get_week_of_issue_integer(self):
    #     week_of_issue = 0
    #     if self.week_of_issue == 'one':
    #         week_of_issue = 1
    #     if self.week_of_issue == 'two':
    #         week_of_issue = 2
    #     if self.week_of_issue == 'three':
    #         week_of_issue = 3
    #     return week_of_issue

class payment_installment(models.Model):
    _name = 'payment.installment'
    _inherit = 'mail.thread'
    _description = 'Payment Installment'

    number = fields.Char('Payment Installment No',required=True)
    name = fields.Char('Name')
    type = fields.Many2one('payment.installment.type',string="Type")
    invoice_id = fields.Many2one('account.invoice',string='Invoice no',required=True)
    currency_id = fields.Many2one('res.currency',related='invoice_id.currency_id')
    amount_due = fields.Monetary('Amount Due')
    origin = fields.Char('Origin')
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    @api.model
    def create_payment_installment_monthly(self):
        types = self.env['payment.installment.type'].search([])
        for type in types:
            invoices = self.env['account.invoice'].search([
                ('installment_type_id', '=', type.id),
                ('installment_count', '<', int(type.duration))
            ])
            for invoice in invoices:
                day_now = now.date().strftime('%Y-%m-%d')
                if invoice.next_date_create_installment == day_now:
                    payment_installment = self.create_payment_installment(invoice.id)

                    activity_type_id = self.env['mail.activity.type'].search([('name', '=', 'Payment Installment')])
                    if not activity_type_id:
                        activity_type_id = self.env['mail.activity.type'].create(
                            {'name': 'Payment Installment', 'summary': 'Follow up Payment Installment Entries'})

                    model_id = self.env['ir.model'].search([('model', '=', 'payment.installment')])
                    activity_vals = {
                        'user_id': payment_installment.invoice_id.user_id and payment_installment.invoice_id.user_id.id or False,
                        'date_deadline': datetime.datetime.today(),
                        'activity_type_id': activity_type_id and activity_type_id[0].id,
                        'note': "<p>Payment Installment: " + str(payment_installment.name)+ " </p>",
                        'res_id': payment_installment.id,
                        'res_model': 'payment.installment',
                        'res_model_id': model_id.id,
                        'summary': activity_type_id.summary
                    }
                    self.env['mail.activity'].create(activity_vals)

    @api.model
    def create_payment_installment(self,invoice_id):
        invoice = self.env['account.invoice'].browse(invoice_id)
        st_count = str(invoice.installment_count + 1) if invoice.installment_count >= 9 else '0'+str(invoice.installment_count + 1)
        number = 'ST' + st_count + '/' + invoice.number
        vals = {
            'name': number,
            'number': number,
            'type': invoice.installment_type_id.id,
            'invoice_id': invoice.id,
            'amount_due': (invoice.amount_total / int(invoice.installment_type_id.duration)),
            'origin': invoice.origin,
            'sale_order_id': invoice.sale_order_id and invoice.sale_order_id.id or False,
        }
        payment_installment = self.env['payment.installment'].create(vals)
        invoice.installment_count += 1
        invoice.next_date_create_installment = invoice.get_next_date_create_installment(now.date().strftime('%Y-%m-%d'))
        return payment_installment


class paymentinstallment(models.Model):
    _name = "payment.installment"
    _inherit = ['payment.installment', 'mail.activity.mixin']


class sale_order(models.Model):
    _inherit = "sale.order"

    payment_installment_type = fields.Many2one('payment.installment.type', string="Payment Installment")
    payment_installment_count = fields.Integer(string='number payment', compute='_compute_count_payment_installment')

    @api.depends('payment_installment_type')
    def _compute_count_payment_installment(self):
        for order in self:
            order.payment_installment_count = self.env['payment.installment'].sudo().search_count([('sale_order_id', '=', order.id)])

    @api.multi
    def action_installment(self):
        True


class sale_advance_payment_inv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    payment_installment_type = fields.Many2one('payment.installment.type', string="Payment Installment")

    @api.model
    def default_get(self, fields):
        result = super(sale_advance_payment_inv, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(active_id)
        if sale_order.payment_installment_type:
            result.update({
                'advance_payment_method': 'delivered',
                'payment_installment_type' : sale_order.payment_installment_type.id
            })
        return result