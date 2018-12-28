from odoo import api, fields, models


class Job(models.Model):
    _inherit = 'hr.job'

    expense_product_ids = fields.One2many('expense.product', 'hr_job_id', string='Expense Products')
    
    
class ExpenseProduct(models.Model):
    
    _name = 'expense.product'
    
    product_id = fields.Many2one('product.product', string='Product', domain=[('can_be_expensed', '=', True)])
    maximum_amount = fields.Integer(string='Maximum Amount')
    hr_job_id = fields.Many2one('hr.job', string='Job')

class hr_contract(models.Model):
    
    _inherit = 'hr.contract'
    
    @api.onchange('job_id')
    def _compute_job_id(self):
        for contract in self:
            hr_cont_prod_list = []
            for expense_product in contract.job_id.expense_product_ids:
                hr_cont_prod_list.append((0, 0, {
                    'product_id': expense_product.product_id.id,
                    'max_prod_cap': expense_product.maximum_amount,
                    'start_date': contract.date_start,
                    'end_date': contract.date_end,
                }))
            contract.hr_cont_prod_ids = hr_cont_prod_list