import logging

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Holidays(models.Model):
    _inherit = "hr.holidays"

    @api.depends('leave_manager_id')
    def _check_leave_manager_id(self):
        for holiday in self:
            if holiday.leave_manager_id.id == self.env.uid:
                self.check_leave_manager = True
            else:
                self.check_leave_manager = False

    leave_manager_id = fields.Many2one('res.users', string='Leave Manager')
    check_leave_manager = fields.Boolean(compute='_check_leave_manager_id', )
    state = fields.Selection([('draft', 'New'), ('confirm', 'Waiting Pre-Approval'), ('refuse', 'Refused'),
                              ('validate2', 'Waiting Approval'),
                              ('validate1', 'Waiting Final Approval'), ('validate', 'Approved'),
                              ('cancel', 'Cancelled')],
                             'State', readonly=True, help='The state is set to \'Draft\', when a holiday request is created.\
           \nThe state is \'Waiting Approval\', when holiday request is confirmed by user.\
           \nThe state is \'Refused\', when holiday request is refused by manager.\
           \nThe state is \'Approved\', when holiday request is approved by manager.')

    @api.model
    def create(self, values):
        employee = self.env['hr.employee'].browse(values.get('employee_id'))
        if not employee.leave_manager:
            raise AccessError(_('You cannot set a leave request with out set leave manager.'))
        leave_manager = employee.leave_manager
        values.update({
            'leave_manager_id': leave_manager.user_id.id
        })
        holiday = super(Holidays, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(
            values)
        holiday.write({'state': 'confirm'})
        return holiday

    @api.multi
    def write(self, values):
        for record in self:
            employee = record.employee_id
            if not employee.leave_manager:
                raise AccessError(_('You cannot set a leave request with out set leave manager.'))
            leave_manager = employee.leave_manager
            values.update({
                'leave_manager_id': leave_manager.user_id.id,
            })
            result = super(Holidays, self).write(values)
            return result

    @api.multi
    def action_leave_manager_approve(self):
        for holiday in self:
            return holiday.write({'state': 'validate2'})

    @api.multi
    def action_confirm(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
        return self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state != 'validate2':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

class Employee(models.Model):
    _inherit = "hr.employee"

    current_leave_state = fields.Selection([('draft', 'New'), ('confirm', 'Waiting Approval'),
                                            ('refuse', 'Refused'), ('validate2', 'Waiting Approval'),
                                            ('validate1', 'Waiting Second Approval'), ('validate', 'Approved'),
                                            ('cancel', 'Cancelled')], compute='compute_leave_status',
                                           string="Current Leave Status", )
    current_leave_id = fields.Many2one('hr.holidays.status', compute='compute_leave_status',
                                       string="Current Leave Type")
    leave_date_from = fields.Date('From Date', compute='compute_leave_status')
    leave_date_to = fields.Date('To Date', compute='compute_leave_status')

    @api.multi
    def compute_leave_status(self):
        # Used SUPERUSER_ID to forcefully get status of other user's leave, to bypass record rule
        holidays = self.env['hr.holidays'].sudo().search([
            ('employee_id', 'in', self.ids),
            ('date_from', '<=', fields.Datetime.now()),
            ('date_to', '>=', fields.Datetime.now()),
            ('type', '=', 'remove'),
            ('state', 'not in', ('cancel', 'refuse'))
        ])
        leave_data = {}
        for holiday in holidays:
            leave_data[holiday.employee_id.id] = {}
            leave_data[holiday.employee_id.id]['leave_date_from'] = holiday.date_from
            leave_data[holiday.employee_id.id]['leave_date_to'] = holiday.date_to
            leave_data[holiday.employee_id.id]['current_leave_state'] = holiday.state
            leave_data[holiday.employee_id.id]['current_leave_id'] = holiday.holiday_status_id.id

        for employee in self:
            employee.leave_date_from = leave_data.get(employee.id, {}).get('leave_date_from')
            employee.leave_date_to = leave_data.get(employee.id, {}).get('leave_date_to')
            employee.current_leave_state = leave_data.get(employee.id, {}).get('current_leave_state')
            employee.current_leave_id = leave_data.get(employee.id, {}).get('current_leave_id')