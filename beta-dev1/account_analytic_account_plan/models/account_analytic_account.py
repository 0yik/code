# -*- coding: utf-8 -*-

from odoo import models, fields, api

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    analytic_ctg = fields.Many2one('account.analytic.category', string='Analytic Category')
    general_distribution = fields.Float('General Distribution %', digits=(6, 2), compute='_compute_general_distribution', readonly=False)
    # general_distribution = fields.Function('_compute_general_distribution',type="float",string='General Distribution %', digits=(6, 2), readonly=False)


    @api.multi
    def _compute_general_distribution(self):
        for record in self:
            if record.analytic_ctg.name == 'Department':
                emp_total = len(self.env['hr.employee'].search([]))
                if record.name:
                    department_id = self.env['hr.department'].search([('name','=',record.name)], limit=1)
                    if department_id and department_id.num_emp:
                        record.general_distribution = (float(department_id.num_emp) / float(emp_total))* 100

class account_analytic_line(models.Model):
    _inherit ='account.analytic.line'

    analytic_ctg_id = fields.Many2one('account.analytic.category', string='Analytic Category',
                                      related='account_id.analytic_ctg', store=True, readonly=1)