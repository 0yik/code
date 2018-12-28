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

from odoo import fields, models, exceptions
from odoo.tools.translate import _

class hr_so_project(models.TransientModel):
    _name = 'hr.sign.out.project'
    _description = 'Sign Out By Project'

    account_id = fields.Many2one('account.analytic.account', 'Project / Analytic Account',
                                 domain=[('type', '=', 'normal')])
    info = fields.Char('Work Description', required=True)
    date_start = fields.Datetime('Starting Date', readonly=True)
    date = fields.Datetime('Closing Date')
    analytic_amount = fields.Float('Minimum Analytic Amount')
    name = fields.Char('Employee\'s Name', required=True, readonly=True)
    state = fields.Selection(related='emp_id.state', string='Current Status',
                             selection=[('present', 'Present'), ('absent', 'Absent')], required=True, readonly=True)
    server_date = fields.Datetime('Current Date', required=True, readonly=True)
    emp_id = fields.Many2one('hr.employee', 'Employee ID')

    def _get_empid(self):
        emp_obj = self.env['hr.employee']
        emp_ids = emp_obj.search([('user_id', '=', self._uid)])
        if emp_ids:
            for employee in emp_obj.browse(emp_ids):
                return {'name': employee.name, 'state': employee.state, 'emp_id': emp_ids[0], 'server_date':time.strftime('%Y-%m-%d %H:%M:%S')}

    def _get_empid2(self):
        res = self._get_empid()
        self._cr.execute('select name,action from hr_attendance where employee_id=%s order by name desc limit 1', (res['emp_id'],))

        res['server_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        date_start = self._cr.fetchone()

        if date_start:
            res['date_start'] = date_start[0]
        return res

    def default_get(self, fields_list):
        res = super(hr_so_project, self).default_get(fields_list)
        res.update(self._get_empid2())
        return res

    def _write(self, data, emp_id, context=None):
        timesheet_obj = self.env['hr.analytic.timesheet']
        emp_obj = self.env['hr.employee']
        if context is None:
            context = {}
        hour = (time.mktime(time.strptime(data['date'] or time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')) -
            time.mktime(time.strptime(data['date_start'], '%Y-%m-%d %H:%M:%S'))) / 3600.0
        minimum = data['analytic_amount']
        if minimum:
            hour = round(round((hour + minimum / 2) / minimum) * minimum, 2)
        res = timesheet_obj.default_get(['product_id','product_uom_id'])

        if not res['product_uom_id']:
            raise exceptions.Warning(_('User Error!'), _('Please define cost unit for this employee.'))
        up = timesheet_obj.on_change_unit_amount(False, res['product_id'], hour,False, res['product_uom_id'])['value']

        res['name'] = data['info']
        res['account_id'] = data['account_id'].id
        res['unit_amount'] = hour
        emp_journal = emp_obj.browse(emp_id).journal_id
        res['journal_id'] = emp_journal and emp_journal.id or False
        res.update(up)
        up = timesheet_obj.on_change_account_id(res['account_id']).get('value', {})
        res.update(up)
        return timesheet_obj.create(res)

    def sign_out_result_end(self):
        emp_obj = self.env['hr.employee']
        for data in self:
            emp_id = data.emp_id.id
            emp_obj.attendance_action_change([emp_id], {'action':'sign_out', 'action_date':data.date})
            data._write(data, emp_id)
        return {'type': 'ir.actions.act_window_close'}

    def sign_out_result(self):
        emp_obj = self.env['hr.employee']
        for data in self:
            emp_id = data.emp_id.id
            emp_obj.attendance_action_change([emp_id], {'action':'action', 'action_date':data.date})
            self._write(data, emp_id)
        return {'type': 'ir.actions.act_window_close'}


class hr_si_project(models.TransientModel):

    _name = 'hr.sign.in.project'
    _description = 'Sign In By Project'

    name = fields.Char('Employee\'s Name', readonly=True)
    state = fields.Selection(related='emp_id.state', string='Current Status',
                             selection=[('present', 'Present'), ('absent', 'Absent')], required=True, readonly=True)
    date = fields.Datetime('Starting Date')
    server_date = fields.Datetime('Current Date', readonly=True)
    emp_id = fields.Many2one('hr.employee', 'Employee ID')

    def view_init(self):
        """
        This function checks for precondition before wizard executes
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param fields: List of fields for default value
        @param context: A standard dictionary for contextual values
        """
        emp_obj = self.env['hr.employee']
        emp_id = emp_obj.search([('user_id', '=', self._uid)])
        if not emp_id:
            raise exceptions.Warning(_('User Error!'), _('Please define employee for your user.'))
        return False

    def check_state(self):
        obj_model = self.env['ir.model.data']
        emp_id = self.default_get(['emp_id'])['emp_id']
        # get the latest action (sign_in or out) for this employee
        self._cr.execute('select action from hr_attendance where employee_id=%s and action in (\'sign_in\',\'sign_out\') order by name desc limit 1', (emp_id,))
        res = (self._cr.fetchone() or ('sign_out',))[0]
        in_out = (res == 'sign_out') and 'in' or 'out'
        #TODO: invert sign_in et sign_out
        model_data_ids = obj_model.search([('model','=','ir.ui.view'),('name','=','view_hr_timesheet_sign_%s' % in_out)])
        resource_id = obj_model.read(model_data_ids, fields=['res_id'])[0]['res_id']
        return {
            'name': _('Sign in / Sign out'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.sign.%s.project' % in_out,
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def sign_in_result(self):
        emp_obj = self.env['hr.employee']
        for data in self:
            emp_id = data.emp_id.id
            emp_obj.attendance_action_change([emp_id], {'action':'sign_in', 'action_date':data.date})
        return {'type': 'ir.actions.act_window_close'}

    def default_get(self):
        res = super(hr_si_project, self).default_get()
        emp_obj = self.env['hr.employee']
        emp_id = emp_obj.search([('user_id', '=', self._uid)])
        if emp_id:
            for employee in emp_obj.browse(emp_id):
                res.update({'name': employee.name, 'state': employee.state, 'emp_id': emp_id[0], 'server_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
