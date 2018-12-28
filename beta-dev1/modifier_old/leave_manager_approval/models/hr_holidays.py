from odoo import api, fields, models, _
from odoo.exceptions import UserError

HOURS_PER_DAY = 8

class Hr_Holidays(models.Model):
    _inherit = 'hr.holidays'

    def _default_manager(self):
        return self.env.user.employee_ids and self.env.user.employee_ids[0].parent_id.id or False

    no_of_approval = fields.Selection(related='employee_id.no_of_approval',readonly=True,string='Number of Approvals Needed')
    total_approval = fields.Integer('Total Approvals Done')
    next_manager_user_id = fields.Many2one(related='next_manager_id.user_id',string='Next Approval User')
    next_manager_id = fields.Many2one('hr.employee', string='Next Approval By', default=_default_manager)

    @api.onchange('employee_id')
    def onchange_employee(self):
        for record in self:
            record.next_manager_id = record.employee_id and record.employee_id.parent_id.id or False

    @api.multi
    def _remove_resource_leave(self):
        """ This method will create entry in resource calendar leave object at the time of holidays cancel/removed """
        return self.env['resource.calendar.leaves'].search([('holiday_id', 'in', self.ids)]).unlink()

    @api.multi
    def action_draft(self):
        for holiday in self:
            if not holiday.can_reset:
                raise UserError(_('Only an HR Manager or the concerned employee can reset to draft.'))
            holiday.write({
                'state': 'draft',
                'next_manager_id': self.employee_id and self.employee_id.parent_id.id or False,
                'total_approval': 0,
            })
            linked_requests = holiday.mapped('linked_request_ids')
            for linked_request in linked_requests:
                linked_request.action_draft()
            linked_requests.unlink()
        return True

    @api.multi
    def action_approve(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        for holiday in self:
            if (holiday.next_manager_id.id) and (self.env.user.id == holiday.next_manager_user_id.id):
                holiday.write({'next_manager_id': self.env.user.employee_ids[0].parent_id.id,'total_approval': holiday.total_approval + 1})
            else:
                raise UserError(_('Need to approve by '+ str(self.next_manager_user_id.name)))

            if (holiday.no_of_approval == holiday.total_approval) or (holiday.next_manager_id.id == False):
                holiday.write({'state':'validate'})
                holiday.action_validate()

    @api.multi
    def action_validate(self):
        for holiday in self:
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [
                        (6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',  # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                # Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
        return True

    @api.multi
    def action_refuse(self):
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))

        for holiday in self:
            holiday.write({'state':'refuse'})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        return True

Hr_Holidays()