from odoo import models, fields, api

class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    
    @api.multi
    def _get_upcoming_spent_amount(self):
        for record in self:
            #Here, if any Purchase is validated and still not invoiced or its invoice is still not validated,
            #its amount will be set as Upcoming
            #once Purchase invoice will be validated, spent amount will be increase and upcoming will be down.
            upcoming = spent = 0.0
            purchase_lines = self.env['purchase.order.line'].search([('account_analytic_id','=',record.id),('order_id.state','in',['purchase','done'])])
            for line in purchase_lines:
                invoice_lines = filter(lambda x:x.invoice_id.state in ['open','paid'],line.invoice_lines)
                if not invoice_lines:
                    upcoming += line.price_subtotal
                                 
            invoice_lines = self.env['account.invoice.line'].search([('account_analytic_id','=',record.id),('invoice_id.state','in',['open','paid'])])
            for line in invoice_lines:
                spent += line.price_subtotal
            
            record.spent_amount = round(spent,2)
            record.upcoming_amount = round(upcoming,2)
                                
    expected_amount = fields.Float('Expected Amount')
    spent_amount = fields.Float(compute='_get_upcoming_spent_amount',string='Spent')
    upcoming_amount = fields.Float(compute='_get_upcoming_spent_amount',string='Upcoming')