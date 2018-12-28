# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from odoo import fields, models, api, exceptions
from odoo.tools.translate import _
import odoo

class hr_employee(models.Model):
    _name = "hr.employee"
    _inherit = "hr.employee"

    product_id = fields.Many2one('product.product', 'Product',
                                 help="If you want to reinvoice working time of employees, link this employee to a service to determinate the cost price of the job.")
    journal_id = fields.Many2one('account.analytic.journal', 'Analytic Journal')
    uom_id = fields.Many2one(related='product_id.uom_id', relation='product.uom', string='Unit of Measure', store=True,
                             readonly=True)

    def _getAnalyticJournal(self):
        md = self.env['ir.model.data']
        try:
            dummy, res_id = md.get_object_reference('hr_timesheet', 'analytic_journal')
            #search on id found in result to check if current user has read access right
            check_right = self.env['account.analytic.journal'].search([('id', '=', res_id)])
            if check_right:
                return res_id
        except ValueError:
            pass
        return False

    def _getEmployeeProduct(self):
        md = self.env['ir.model.data']
        try:
            dummy, res_id = md.get_object_reference('product', 'product_product_consultant')
            #search on id found in result to check if current user has read access right
            check_right = self.env['product.template'].search([('id', '=', res_id)])
            if check_right:
                return res_id
        except ValueError:
            pass
        return False

    _defaults = {
        'journal_id': _getAnalyticJournal,
        'product_id': _getEmployeeProduct
    }


class hr_analytic_timesheet(models.Model):
    _name = "hr.analytic.timesheet"
    _table = 'hr_analytic_timesheet'
    _description = "Timesheet Line"
    _inherits = {'account.analytic.line': 'line_id'}
    _order = "id desc"

    line_id = fields.Many2one('account.analytic.line', 'Analytic Line', ondelete='cascade', required=True)
    partner_id = fields.Many2one(related='account_id.partner_id', string='Partner', relation='res.partner', store=True)

    @api.multi
    def unlink(self):
        toremove = {}
        for obj in self:
            toremove[obj.line_id.id] = True
        super(hr_analytic_timesheet, self).unlink()
        self.env['account.analytic.line'].unlink(toremove.keys())
        return True


    def on_change_unit_amount(self, prod_id, unit_amount, company_id, unit=False, journal_id=False):
        res = {'value':{}}
        if prod_id and unit_amount:
            # find company
            company_id = self.env['res.company']._company_default_get('account.analytic.line')
            r = self.env['account.analytic.line'].on_change_unit_amount(prod_id, unit_amount, company_id, unit, journal_id)
            if r:
                res.update(r)
        # update unit of measurement
        if prod_id:
            uom = self.env['product.product'].browse(prod_id)
            if uom.uom_id:
                res['value'].update({'product_uom_id': uom.uom_id.id})
        else:
            res['value'].update({'product_uom_id': False})
        return res

    def _getEmployeeProduct(self):
        context = {}
        emp_obj = self.env['hr.employee']
        emp_id = emp_obj.search([('user_id', '=', context.get('user_id') or self._uid)])
        if emp_id:
            emp = emp_obj.browse(emp_id[0])
            if emp.product_id:
                return emp.product_id.id
        return False

    def _getEmployeeUnit(self):
        emp_obj = self.env['hr.employee']
        context = {}
        emp_id = emp_obj.search([('user_id', '=', context.get('user_id') or self._uid)])
        if emp_id:
            emp = emp_obj.browse(emp_id[0])
            if emp.product_id:
                return emp.product_id.uom_id.id
        return False

    def _getGeneralAccount(self):
        emp_obj = self.env['hr.employee']
        context = {}
        emp_id = emp_obj.search([('user_id', '=', context.get('user_id') or self._uid)])
        if emp_id:
            emp = emp_obj.browse(emp_id[0])
            if bool(emp.product_id):
                a = emp.product_id.property_account_expense.id
                if not a:
                    a = emp.product_id.categ_id.property_account_expense_categ.id
                if a:
                    return a
        return False

    def _getAnalyticJournal(self):
        emp_obj = self.env['hr.employee']
        context = {}
        if context.get('employee_id'):
            emp_id = [context.get('employee_id')]
        else:
            emp_id = emp_obj.search([('user_id','=',context.get('user_id') or self._uid)], limit=1)
        if not emp_id:
            model, action_id = self.env['ir.model.data'].get_object_reference('hr', 'open_view_employee_list_my')
            msg = _("Employee is not created for this user. Please create one from configuration panel.")
            raise exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        emp = emp_obj.browse(emp_id[0])
        if emp.journal_id:
            return emp.journal_id.id
        else :
            raise exceptions.Warning(_('Warning!'), _('No analytic journal defined for \'%s\'.\nYou should assign an analytic journal on the employee form.')%(emp.name))


    _defaults = {
        'product_uom_id': _getEmployeeUnit,
        'product_id': _getEmployeeProduct,
        'general_account_id': _getGeneralAccount,
        'journal_id': _getAnalyticJournal,
        'date': lambda self, cr, uid, ctx: ctx.get('date', fields.date.context_today(self,cr,uid,context=ctx)),
        'user_id': lambda obj, cr, uid, ctx: ctx.get('user_id') or uid,
    }
    def on_change_account_id(self, account_id):
        return {'value':{}}

    def on_change_date(self, date):
        if self._ids:
            new_date = self.read(['date'])['date']
            if date != new_date:
                warning = {'title':_('User Alert!'),'message':_('Changing the date will let this entry appear in the timesheet of the new date.')}
                return {'value':{},'warning':warning}
        return {'value':{}}

    def create(self, vals):
        context = {}
        emp_obj = self.env['hr.employee']
        emp_id = emp_obj.search([('user_id', '=', context.get('user_id') or self._uid)])
        ename = ''
        if emp_id:
            ename = emp_obj.browse(emp_id[0]).name
        if not vals.get('journal_id',False):
           raise exceptions.Warning(_('Warning!'), _('No \'Analytic Journal\' is defined for employee %s \nDefine an employee for the selected user and assign an \'Analytic Journal\'!')%(ename,))
        if not vals.get('account_id',False):
           raise exceptions.Warning(_('Warning!'), _('No analytic account is defined on the project.\nPlease set one or we cannot automatically fill the timesheet.'))
        return super(hr_analytic_timesheet, self).create(vals)

    def on_change_user_id(self, user_id):
        if not user_id:
            return {}
        context = {'user_id': user_id}
        return {'value': {
            'product_id': self._getEmployeeProduct(),
            'product_uom_id': self._getEmployeeUnit(),
            'general_account_id': self._getGeneralAccount(),
            'journal_id': self._getAnalyticJournal(),
        }}

class account_analytic_account(models.Model):

    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    use_timesheets = fields.Boolean('Timesheets', help="Check this field if this project manages timesheets")

    def on_change_template(self, template_id, date_start=False):
        res = super(account_analytic_account, self).on_change_template(template_id, date_start=date_start)
        if template_id and 'value' in res:
            template = self.browse(template_id)
            res['value']['use_timesheets'] = template.use_timesheets
        return res

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    task_id = fields.Many2one('project.task', 'Task')
    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])
    # department_id = fields.Many2one('hr.department', "Department", related='user_id.employee_ids.department_id',
    #                                 store=True, readonly=True)

    @api.onchange('project_id')
    def onchange_project_id(self):
        self.task_id = False

    @api.model
    def create(self, vals):
        if vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['account_id'] = project.analytic_account_id.id
        return super(AccountAnalyticLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('project_id'):
            project = self.env['project.project'].browse(vals.get('project_id'))
            vals['account_id'] = project.analytic_account_id.id
        return super(AccountAnalyticLine, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
