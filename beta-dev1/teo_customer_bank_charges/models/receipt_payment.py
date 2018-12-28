from odoo import models, fields, api
 

class ReceiptPayment(models.Model):
    _inherit = 'receipt.payment'
	
    expense_account = fields.Many2one('account.account', string='Expense Account')
    charge_amount = fields.Float(string='Amount')
    description = fields.Text(string='Description')
