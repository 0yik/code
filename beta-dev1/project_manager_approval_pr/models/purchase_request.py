from odoo import models, fields, api


class purchase_request(models.Model):
    _inherit = 'purchase.request'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    check_access_request = fields.Boolean('Check Approval', compute='_compute_check_access_analytic_account',
                                          default=False)

    @api.one
    @api.depends('account_analytic_id', 'requested_by')
    def _compute_check_access_analytic_account(self):
        if self.account_analytic_id and self.account_analytic_id.manager_id:
            if self.account_analytic_id.is_project:
                if self.account_analytic_id.manager_id and self.account_analytic_id.manager_id.id and self.account_analytic_id.manager_id.id != self._uid:
                    self.check_access_request = True
            else:
                if self.requested_by and self.requested_by.id:
                    employee = self.env['hr.employee'].search([('user_id', '=', self.requested_by.id),('parent_id', '!=', False)], limit=1)
                    if employee and employee.id:
                            if employee.parent_id.user_id and employee.parent_id.user_id.id and employee.parent_id.user_id.id != self._uid:
                                self.check_access_request = True

