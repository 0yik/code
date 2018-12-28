
from random import choice
from string import digits

from odoo import models, fields, api, exceptions, _, SUPERUSER_ID

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    breaktime_ids = fields.One2many('emp.breaktime', 'employee_id', help='list of breaktimes for the employee')
    last_breaktime_id = fields.Many2one('emp.breaktime', compute='_compute_last_breaktime_id')
    breaktime_state = fields.Selection(string="Attendance", compute='_compute_breaktime_state',
                                       selection=[('checked_out', "Checked out"), ('checked_in', "Checked in")])
    manual_breaktime = fields.Boolean(string='Manual Break Time', compute='_compute_manual_breaktime', inverse='_inverse_manual_breaktime',
                            help='The employee will have access to the "My Attendances" menu to check in and out from his session')



    @api.multi
    def _compute_manual_breaktime(self):
        for employee in self:
            employee.manual_breaktime = employee.user_id.has_group('hr.group_hr_attendance') if employee.user_id else False

    @api.multi
    def _inverse_manual_breaktime(self):
        manual_attendance_group = self.env.ref('hr.group_hr_attendance')
        for employee in self:
            if employee.user_id:
                if employee.manual_breaktime:
                    manual_attendance_group.users = [(4, employee.user_id.id, 0)]
                else:
                    manual_attendance_group.users = [(3, employee.user_id.id, 0)]


    @api.depends('breaktime_ids')
    def _compute_last_breaktime_id(self):
        for employee in self:
            employee.last_breaktime_id = employee.breaktime_ids and employee.breaktime_ids[0] or False

    @api.depends('last_breaktime_id.check_in', 'last_breaktime_id.check_out', 'last_breaktime_id')
    def _compute_breaktime_state(self):
        for employee in self:
            employee.breaktime_state = employee.last_breaktime_id and not employee.last_breaktime_id.check_out and 'checked_in' or 'checked_out'


    @api.model
    def breaktime_scan(self, barcode):
        """ Receive a barcode scanned from the Kiosk Mode and change the breaktime of corresponding employee.
            Returns either an action or a warning.
        """
        employee = self.search([('barcode', '=', barcode)], limit=1)
        return employee and employee.breaktime_action('employee_breaktime.employee_breaktime_action_kiosk_mode') or \
               {'warning': _('No employee corresponding to barcode %(barcode)s') % {'barcode': barcode}}

    @api.multi
    def breaktime_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        if not (entered_pin is None) or self.env['res.users'].browse(SUPERUSER_ID).has_group(
                'hr_attendance.group_hr_attendance_use_pin') and (
                self.user_id and self.user_id.id != self._uid or not self.user_id):
            if entered_pin != self.pin:
                return {'warning': _('Wrong PIN')}
        return self.breaktime_action(next_action)

    @api.multi
    def breaktime_action(self, next_action):
        """ Changes the breaktime of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My breaktime" or "Kiosk Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('employee_breaktime.emp_breaktime_action_greeting_message').read()[0]
        action_message['previous_breaktime_change_date'] = self.last_breaktime_id and (
                    self.last_breaktime_id.check_out or self.last_breaktime_id.check_in) or False
        action_message['employee_name'] = self.name
        action_message['next_action'] = next_action

        if self.user_id:
            modified_breaktime = self.sudo(self.user_id.id).breaktime_action_change()
        else:
            modified_breaktime = self.sudo().breaktime_action_change()
        action_message['breaktime'] = modified_breaktime.read()[0]
        return {'action': action_message}

    @api.multi
    def breaktime_action_change(self):
        """ Check In/Check Out action
            Check In: create a new breaktime record
            Check Out: modify check_out field of appropriate breaktime record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date = fields.Datetime.now()

        if self.breaktime_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
            }
            return self.env['emp.breaktime'].create(vals)
        else:
            breaktime = self.env['emp.breaktime'].search([('employee_id', '=', self.id), ('check_out', '=', False)],
                                                          limit=1)
            if breaktime:
                breaktime.check_out = action_date
            else:
                raise exceptions.UserError(
                    _('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                      'Your breaktime have probably been modified manually by human resources.') % {
                        'empl_name': self.name, })
            return breaktime

