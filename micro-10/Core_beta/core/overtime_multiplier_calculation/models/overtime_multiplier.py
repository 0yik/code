from odoo import fields,models,api, _
from datetime import datetime
from dateutil import rrule, parser
import logging
import math
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class overtime_multiplier(models.Model):
    
    _name = 'overtime.multiplier'

    name = fields.Char('Code', required=True)
    overtime_name = fields.Char('Name', required=True)
    amount_calculation_method = fields.Selection([
        ('multiply_by_amount', 'Multiply by Amount'),
        ('formula', 'Formula'),
        ('fixed_amount', 'Fixed Amount')
    ], string='Amount Calculation Method', default='multiply_by_amount', required=True)
    multiply_by_amount = fields.Integer()
    formula = fields.Text()
    fixed_amount = fields.Integer()
    overtime_multiplier_rule_ids = fields.One2many("overtime.multiplier.rule", "overtime_multiplier_id", string="Rules") 

class overtime_multiplier_rule(models.Model):
    
    _name = 'overtime.multiplier.rule'
    
    rule_from = fields.Integer("From", required=True)
    rule_to = fields.Integer("To", required=True)
    rule_multiply_by = fields.Float("Multiply By", required=True)
    overtime_multiplier_id = fields.Many2one('overtime.multiplier', string="Overtime Multiplier")
    
class overtime_multiplier(models.Model):
    
    _name = 'overtime.multiplier.employee'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Employee')
    workdays_id = fields.Many2one('overtime.multiplier', string='Work days')
    offdays_id = fields.Many2one('overtime.multiplier', string='Off Days')
    public_holidays_id = fields.Many2one('overtime.multiplier', string='Public Holidays')


class HrPayslipLine(models.Model):

    _inherit = 'hr.payslip.line'

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            overtime_multiplier_employee_id = self.env['overtime.multiplier.employee'].search([('employee_id', '=', line.contract_id.employee_id.id), '|', ('workdays_id.name', '=', line.code), '|', ('offdays_id.name', '=', line.code), ('public_holidays_id.name', '=', line.code)], limit=1)
            if overtime_multiplier_employee_id:
                overtime_multiplier_id = False
                if overtime_multiplier_employee_id.workdays_id.name == line.code:
                    overtime_multiplier_id = overtime_multiplier_employee_id.workdays_id
                elif overtime_multiplier_employee_id.offdays_id.name == line.code:
                    overtime_multiplier_id = overtime_multiplier_employee_id.offdays_id
                elif overtime_multiplier_employee_id.public_holidays_id.name == line.code:
                    overtime_multiplier_id = overtime_multiplier_employee_id.public_holidays_id
                
                if overtime_multiplier_id:
                    overtime_multiplier_rule_id = self.env['overtime.multiplier.rule'].search([('overtime_multiplier_id', '=', overtime_multiplier_id.id), ('rule_from', '<=', line.slip_id.overtime_hours), ('rule_to', '>=', line.slip_id.overtime_hours)])
                    if overtime_multiplier_rule_id:
                        if overtime_multiplier_id.amount_calculation_method == 'multiply_by_amount':
                            line.total =  overtime_multiplier_id.multiply_by_amount * overtime_multiplier_rule_id.rule_multiply_by 
                        elif overtime_multiplier_id.amount_calculation_method == 'formula':
                            line.total =  safe_eval(overtime_multiplier_id.formula)
                        elif overtime_multiplier_id.amount_calculation_method == 'fixed_amount':
                            line.total =  overtime_multiplier_id.fixed_amount
            else:
                line.total = float(line.quantity) * line.amount * line.rate / 100