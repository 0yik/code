from odoo import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    # @api.model
    # def default_get(self, fields):
    #     result = super(account_invoice, self).default_get(fields)
    #     if self.env.context and 'active_id' in self.env.context and 'active_model' in self.env.context \
    #         and self.env.context.get('active_id') and str(self.env.context.get('active_model')) == 'sale.order':
    #         active_id = self.env.context.get('active_id')
    #         sale_order = self.env['sale.order'].browse(active_id)
    #         if sale_order.payment_installment_type:
    #             result.update({
    #                 'installment_type_id': sale_order.payment_installment_type.id
    #                 'sale_order_id': sale_order.id
    #             })
    #     return result

    installment_type_id = fields.Many2one('payment.installment.type', string="Payment Installment Type", copy=False)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", copy=False)
    installment_count = fields.Integer('installment count',default=0, copy=False)
    next_date_create_installment = fields.Date(string='Next day', copy=False)

    @api.multi
    def get_next_date_create_installment(self, date):
        inv_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        last_date = inv_date + relativedelta(months=int(self.installment_type_id.duration))
        total_days = (last_date - inv_date).days
        next_date = inv_date + relativedelta(days=int(round(total_days / int(self.installment_type_id.no_of_installment))))
        return next_date - relativedelta(days=int(self.installment_type_id.days_to_pay))

    @api.multi
    def action_invoice_open(self):
        res = super(account_invoice,self).action_invoice_open()
        if self.origin:
            sale_order = self.env['sale.order'].search([('name','=',self.origin)])
            if sale_order and sale_order.payment_installment_type:
                self.installment_type_id = sale_order.payment_installment_type.id
                self.installment_count = 0
                self.sale_order_id = sale_order.id
                next_date = self.get_next_date_create_installment(self.date_invoice)
                # next_date = datetime.datetime.strptime(self.date_invoice, '%Y-%m-%d') + datetime.timedelta(weeks=self.installment_type_id.get_week_of_issue_integer())
                self.next_date_create_installment = next_date
                self.env['payment.installment'].create_payment_installment_monthly()
        return res