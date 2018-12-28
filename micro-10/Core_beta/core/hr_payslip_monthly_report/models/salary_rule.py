from odoo import fields, models, tools, api

class SalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    appear_on_report = fields.Boolean("Appear on Payslip Report")
