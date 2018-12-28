from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    order_id = fields.Many2one('sale.order', string='SO Document')

class ReconcileDepositWizard(models.TransientModel):
    _inherit = 'account.deposit.reconcile'

    @api.multi
    def reconcile_deposit(self):
        res = super(ReconcileDepositWizard, self).reconcile_deposit()
        if self._context and self._context.get('active_id'):
            pay_id = self.env['account.payment'].search([('id', '=', self._context.get('active_id') )])
            if pay_id and self.invoice_id and self.invoice_id.origin:
                order_id = self.env['sale.order'].search([('name', '=', self.invoice_id.origin)])
                if order_id:
                    pay_id.order_id = order_id
        return res