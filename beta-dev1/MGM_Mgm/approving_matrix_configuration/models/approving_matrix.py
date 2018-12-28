# -*- coding: utf-8 -*-

from odoo import models, fields, api

class approving_matrix_pr(models.Model):
    _name = 'pr.approving.matrix'
    _description = 'Approving Matrix'

    name = fields.Char('Name', required = True)
    line_ids = fields.One2many('pr.approving.matrix.line', 'parent_id', 'Lines',)
    matrix_type = fields.Selection([('amount', 'Applied to Amount'),('sequence', 'Applied to Sequence')], string="Configuration")


class approving_matrix_line_pr(models.Model):
    _name = 'pr.approving.matrix.line'

    name = fields.Char('Name')
    parent_id = fields.Many2one('pr.approving.matrix', 'Matrix ID', ondelete="cascade",)
    employee_ids = fields.Many2many('hr.employee', 'pr_approving_matrix_line_employee_id_rel',
                                    'matrix_line_id', 'employee_id', 'Employee', required=True)
    min_amount = fields.Float('Minimum Amount', required=True, default=0.0)
    max_amount = fields.Float('Maximum Amount')
    approved = fields.Boolean("Approved", copy=False, default=False)
    line_approved = fields.Boolean("Approved", copy=False, default=False)

    matrix_type = fields.Selection([('amount', 'Applied to Amount'), ('sequence', 'Applied to Sequence')],
                                   string="Configuration", related="parent_id.matrix_type")

    @api.model
    def check_amount(self, amount):
        if self.min_amount <= amount:
            if self.max_amount == False or self.max_amount == 0 or self.max_amount >= amount:
                return True
        return False

