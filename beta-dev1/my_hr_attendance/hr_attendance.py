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
from datetime import datetime

from odoo import fields, models, exceptions
from odoo.tools.translate import _


class hr_action_reason(models.Model):
    _name = "hr.action.reason"
    _description = "Action Reason"

    name = fields.Char('Reason', required=True, help='Specifies the reason for Signing In/Signing Out.')
    action_type = fields.Selection([('sign_in', 'Sign in'), ('sign_out', 'Sign out')], "Action Type")

    _defaults = {
        'action_type': 'sign_in',
    }

class hr_attendance(models.Model):
    _name = "hr.attendance"
    _description = "Attendance"

    def _employee_get(self):
        ids = self.env['hr.employee'].search([('user_id', '=', self._uid)])
        return ids and ids[0] or False

    def _worked_hours_compute(self):
        """For each hr.attendance record of action sign-in: assign 0.
        For each hr.attendance record of action sign-out: assign number of hours since last sign-in.
        """
        res = {}
        for obj in self:
            if obj.action == 'sign_in':
                res[obj.id] = 0
            elif obj.action == 'sign_out':
                # Get the associated sign-in
                last_signin = self.search([
                    ('employee_id', '=', obj.employee_id.id),
                    ('name', '<', obj.name), ('action', '=', 'sign_in')
                ], limit=1, order='name DESC')
                if last_signin and len(last_signin)>0:
                    # Compute time elapsed between sign-in and sign-out
                    last_signin_datetime = datetime.strptime(last_signin.name, '%Y-%m-%d %H:%M:%S')
                    signout_datetime = datetime.strptime(obj.name, '%Y-%m-%d %H:%M:%S')
                    workedhours_datetime = (signout_datetime - last_signin_datetime)
                    res[obj.id] = ((workedhours_datetime.seconds) / 60) / 60.0
                else:
                    res[obj.id] = False
        return res

    name = fields.Datetime('Date', required=True, select=1)
    action = fields.Selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action', 'Action')], 'Action',
                              required=True)
    action_desc = fields.Many2one("hr.action.reason", "Action Reason", domain="[('action_type', '=', action)]",
                                  help='Specifies the reason for Signing In/Signing Out in case of extra hours.')
    employee_id = fields.Many2one('hr.employee', "Employee", required=True, select=True)
    worked_hours = fields.Float(compute=_worked_hours_compute, string='Worked Hours', store=True)

    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), #please don't remove the lambda, if you remove it then the current time will not change
        'employee_id': _employee_get,
    }

    def _altern_si_so(self):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
        for att in self:
            # search and browse for first previous and first next records
            prev_atts = self.search([('employee_id', '=', att.employee_id.id), ('name', '<', att.name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name DESC')
            next_atts = self.search([('employee_id', '=', att.employee_id.id), ('name', '>', att.name), ('action', 'in', ('sign_in', 'sign_out'))], limit=1, order='name ASC')
            # check for alternance, return False if at least one condition is not satisfied
            if prev_atts and prev_atts[0].action == att.action: # previous exists and is same action
                return False
            if next_atts and next_atts[0].action == att.action: # next exists and is same action
                return False
            if (not prev_atts) and (not next_atts) and att.action != 'sign_in': # first attendance must be sign_in
                return False
        return True

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]
    _order = 'name desc'


class hr_employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    def _state(self):
        ids = self._ids
        cr = self._cr
        result = {}
        if not ids:
            return result
        for id in ids:
            result[id] = 'absent'
        cr.execute('SELECT hr_attendance.action, hr_attendance.employee_id \
                FROM ( \
                    SELECT MAX(name) AS name, employee_id \
                    FROM hr_attendance \
                    WHERE action in (\'sign_in\', \'sign_out\') \
                    GROUP BY employee_id \
                ) AS foo \
                LEFT JOIN hr_attendance \
                    ON (hr_attendance.employee_id = foo.employee_id \
                        AND hr_attendance.name = foo.name) \
                WHERE hr_attendance.employee_id IN %s',(tuple(ids),))
        for res in cr.fetchall():
            result[res[1]] = res[0] == 'sign_in' and 'present' or 'absent'
        return result

    def _last_sign(self):
        ids = self._ids
        cr = self._cr
        result = {}
        if not ids:
            return result
        for id in ids:
            result[id] = False
            cr.execute("""select max(name) as name
                        from hr_attendance
                        where action in ('sign_in', 'sign_out') and employee_id = %s""",(id,))
            for res in cr.fetchall():
                result[id] = res[0]
        return result

    def _attendance_access(self):
        # this function field use to hide attendance button to singin/singout from menu
        visible = self.env["res.users"].has_group("base.group_hr_attendance")
        return dict([(x, visible) for x in self._ids])

    state = fields.Selection(compute=_state, selection=[('absent', 'Absent'), ('present', 'Present')],
                             string='Attendance')
    last_sign = fields.Datetime(compute=_last_sign, string='Last Sign')
    attendance_access = fields.Boolean(compute=_attendance_access, string='Attendance Access')

    def _action_check(self, emp_id, dt=False, context=None):
        cr = self._cr
        cr.execute('SELECT MAX(name) FROM hr_attendance WHERE employee_id=%s', (emp_id,))
        res = cr.fetchone()
        return not (res and (res[0]>=(dt or time.strftime('%Y-%m-%d %H:%M:%S'))))

    def attendance_action_change(self, context=None):
        if context is None:
            context = {}
        action_date = context.get('action_date', False)
        action = context.get('action', False)
        hr_attendance = self.pool.get('hr.attendance')
        warning_sign = {'sign_in': _('Sign In'), 'sign_out': _('Sign Out')}
        for employee in self:
            if not action:
                if employee.state == 'present': action = 'sign_out'
                if employee.state == 'absent': action = 'sign_in'

            if not self._action_check(employee.id, action_date, context):
                raise exceptions.Warning(_('Warning'), _('You tried to %s with a date anterior to another event !\nTry to contact the HR Manager to correct attendances.')%(warning_sign[action],))

            vals = {'action': action, 'employee_id': employee.id}
            if action_date:
                vals['name'] = action_date
            hr_attendance.create(vals)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
