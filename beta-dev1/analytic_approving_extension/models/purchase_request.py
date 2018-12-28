# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import SUPERUSER_ID
from odoo.exceptions import Warning

class purchase_request(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def get_default_department(self):
        return self.env['hr.employee'].search([('user_id', '=', self._uid),('department_id', '!=', False)], limit=1).department_id.id or False

    product_ctg = fields.Many2one('product.category', string='Product Category', track_visibility='onchange', required=True)
    department_id = fields.Many2one('hr.department', 'Department', track_visibility='onchange', default=get_default_department, required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    check_access_request = fields.Boolean('Check Approval', compute='_compute_check_access_analytic_account', default=False)

    @api.one
    @api.depends('account_analytic_id', 'requested_by')
    def _compute_check_access_analytic_account(self):
        if self.account_analytic_id and self.account_analytic_id.manager_id:
            if self.account_analytic_id.is_project:
                if self.account_analytic_id.manager_id and self.account_analytic_id.manager_id.id and self.account_analytic_id.manager_id.id != self._uid:
                    self.check_access_request = True
            else:
                if self.requested_by and self.requested_by.id:
                    employee = self.env['hr.employee'].search(
                        [('user_id', '=', self.requested_by.id), ('parent_id', '!=', False)], limit=1)
                    if employee and employee.id:
                        if employee.parent_id.user_id and employee.parent_id.user_id.id and employee.parent_id.user_id.id != self._uid:
                            self.check_access_request = True

    @api.multi
    def button_approved(self):
        for record in self:
            if not record.product_ctg or self._uid == SUPERUSER_ID:
                super(purchase_request, record).button_approved()
            else:
                matrix_id = record.get_matrix_id()
                if matrix_id and matrix_id.id:
                    employee_ids = record.compute_access_list(matrix_id)
                    if employee_ids and len(employee_ids) > 0:
                        user_ids = employee_ids.mapped('user_id').ids
                        if self._uid in user_ids :
                            super(purchase_request, record).button_approved()
                        else:
                            raise Warning(_("You don't have access to approve this!"))
                    else:
                        raise Warning(_("Only Administrator can approve this!"))
                else:
                    raise Warning(_("Please setting approving matrix for this Purchase Request!"))

    @api.model
    def compute_access_list(self, matrix_id):
        employee_list = self.env['hr.employee']
        employee_ids = False
        amount = self.compute_amount_for_pr()
        lines = matrix_id.line_ids.filtered(lambda r: r.check_amount(amount) == True)
        for line in lines:
            if line.employee_ids and len(line.employee_ids) > 0:
                employee_ids = line.employee_ids
                if line.job_id and line.job_id.id:
                    if self.department_id and self.department_id.id:
                        employee_ids += employee_list.search(
                            [('department_id', '=', self.department_id.id), ('job_id', '=', line.job_id.id)])
            else:
                if line.job_id and line.job_id.id:
                    if self.department_id and self.department_id.id:
                        employee_ids = employee_list.search(
                            [('department_id', '=', self.department_id.id), ('job_id', '=', line.job_id.id)])
            break
        return employee_ids

    @api.model
    def compute_amount_for_pr(self):
        amount = 0.0
        for line in self.line_ids:
            if line.product_id and line.product_id.id :
                amount += line.product_id.lst_price * line.product_qty
        return amount

    @api.model
    def get_matrix_id(self):
        matrix_obj = self.env['pr.approving.matrix']
        matrix_id = matrix_obj.search([('product_ctg','child_of',[self.product_ctg.id])], limit=1)
        return matrix_id