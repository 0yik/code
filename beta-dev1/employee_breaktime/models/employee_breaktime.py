# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class EmpBreakTime(models.Model):
    _name = "emp.breaktime"
    _description = "Breaktime"
    _order = "check_in desc"

    def _default_employee(self):
        return self.env['emp.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id")
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Break Hours', compute='_compute_worked_hours', store=True, readonly=True)

    @api.multi
    def name_get(self):
        result = []
        for breaktime in self:
            if not breaktime.check_out:
                result.append((breaktime.id, _("%(empl_name)s from %(check_in)s") % {
                    'empl_name': breaktime.employee_id.name_related,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(breaktime, fields.Datetime.from_string(breaktime.check_in))),
                }))
            else:
                result.append((breaktime.id, _("%(empl_name)s from %(check_in)s to %(check_out)s") % {
                    'empl_name': breaktime.employee_id.name_related,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(breaktime, fields.Datetime.from_string(breaktime.check_in))),
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(breaktime, fields.Datetime.from_string(breaktime.check_out))),
                }))
        return result

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for breaktime in self:
            if breaktime.check_out:
                delta = datetime.strptime(breaktime.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    breaktime.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                breaktime.worked_hours = delta.total_seconds() / 3600.0

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for breaktime in self:
            if breaktime.check_in and breaktime.check_out:
                if breaktime.check_out < breaktime.check_in:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the breaktime record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" breaktime record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for breaktime in self:
            # we take the latest breaktime before our check_in time and check it doesn't overlap with ours
            last_breaktime_before_check_in = self.env['emp.breaktime'].search([
                ('employee_id', '=', breaktime.employee_id.id),
                ('check_in', '<=', breaktime.check_in),
                ('id', '!=', breaktime.id),
            ], order='check_in desc', limit=1)
            if last_breaktime_before_check_in and last_breaktime_before_check_in.check_out and last_breaktime_before_check_in.check_out > breaktime.check_in:
                raise exceptions.ValidationError(_("Cannot create new breaktime record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': breaktime.employee_id.name_related,
                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(breaktime.check_in))),
                })

            if not breaktime.check_out:
                # if our breaktime is "open" (no check_out), we verify there is no other "open" breaktime
                no_check_out_breaktimes = self.env['emp.breaktime'].search([
                    ('employee_id', '=', breaktime.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', breaktime.id),
                ])
                if no_check_out_breaktimes:
                    raise exceptions.ValidationError(_("Cannot create new breaktime record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': breaktime.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_breaktimes.check_in))),
                    })
            else:
                # we verify that the latest breaktime with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_breaktime_before_check_out = self.env['emp.breaktime'].search([
                    ('employee_id', '=', breaktime.employee_id.id),
                    ('check_in', '<', breaktime.check_out),
                    ('id', '!=', breaktime.id),
                ], order='check_in desc', limit=1)
                if last_breaktime_before_check_out and last_breaktime_before_check_in != last_breaktime_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new breaktime record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': breaktime.employee_id.name_related,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_breaktime_before_check_out.check_in))),
                    })

    @api.multi
    def copy(self):
        raise exceptions.UserError(_('You cannot duplicate any Breaktime.'))
