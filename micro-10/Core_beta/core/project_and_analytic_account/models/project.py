from odoo import api, fields, models, tools

class Project(models.Model):
    _inherit='project.project'
    
    budgeted_cost = fields.Float(related='analytic_account_id.expected_amount',string="Budgeted Cost")
    spent_budget = fields.Float(related='analytic_account_id.spent_amount',string="Spent Budget")