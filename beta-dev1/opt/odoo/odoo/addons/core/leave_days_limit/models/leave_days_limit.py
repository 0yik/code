from odoo import api, fields, models,_
import math
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta

HOURS_PER_DAY = 8

class LeaveDaysLimit(models.Model):
    _name = 'leave.days.limit'
    _inherit = ['mail.thread']
    _description = 'Leave Days Limit'
    _rec_name = 'no_of_days'
    _order = "id desc"

    no_of_days = fields.Integer(string='Number Of Days',track_visibility='onchange')
    leave_type_line_ids = fields.One2many('leave.days.limit.line','leave_type_line_id','Leave Types')

LeaveDaysLimit()

class LeaveDaysLimitLine(models.Model):
    _name = 'leave.days.limit.line'
    _description = 'Leave Days Limit Line'

    leave_type_line_id = fields.Many2one('leave.days.limit',string='Leave Type Line Id')
    leave_type_id = fields.Many2one('hr.holidays.status',string='Leave Types')

    @api.onchange('leave_type_id')
    def onchange_leave_type(self):
        warning = {}
        if self.leave_type_id and (self.leave_type_id.name2 == 'Sick Leaves' or self.leave_type_id.name2 == 'Hospitalisation Leave'):
            self.leave_type_id = False
            warning = {'message': "Sorry!\nCannot apply leave limit for Sick Leaves/Hospitalisation Leave"}
        return {'warning': warning}

LeaveDaysLimitLine()

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def action_approve(self):
        leave_type_ids = self.env['leave.days.limit'].search([('leave_type_line_ids.leave_type_id.id', '=', self.holiday_status_id.id)])
        for holiday in self:
            if holiday.type == 'remove':
                for leave_type_line in leave_type_ids.leave_type_line_ids:
                    current_date = datetime.today()
                    if (leave_type_line.leave_type_line_id and leave_type_line.leave_type_line_id.no_of_days) and leave_type_ids.id:
                        working_days_to_add = leave_type_line.leave_type_line_id.no_of_days
                        holiday_list = []
                        public_holiday_ids = self.env['hr.holiday.public'].search([('state', '=', 'validated')])
                        for public_holiday_record in public_holiday_ids:
                            for holidays in public_holiday_record.holiday_line_ids:
                                date = datetime.strptime(holidays.holiday_date, '%Y-%m-%d').strftime("%Y-%m-%d")
                                holiday_list.append(date)
                            # Check no. of days
                            while working_days_to_add > 0:
                                current_date += relativedelta(days=1)
                                weekday = current_date.weekday()
                                # Check if weekday is saturday or sunday and check if current date is public holiday
                                if weekday >= 5 and current_date.strftime("%Y-%m-%d") in holiday_list:
                                    continue
                                # Check if weekday is saturday or sunday
                                elif weekday >= 5:
                                    continue
                                #check if current date is public holiday
                                elif current_date.strftime("%Y-%m-%d") in holiday_list:
                                    continue
                                working_days_to_add -= 1
                            final_date = current_date + relativedelta(days = working_days_to_add)
                            date_from = False
                            if holiday.date_from:
                                date_from = str(datetime.strptime(holiday.date_from, DEFAULT_SERVER_DATETIME_FORMAT))
                            if date_from < str(datetime.strftime(final_date, DEFAULT_SERVER_DATETIME_FORMAT)):
                                raise UserError('Sorry!\n ' +holiday.holiday_status_id.name2+ ' has to be applied before ' +str(leave_type_line.leave_type_line_id.no_of_days)+ ' working day(s).')
        return super(HrHolidays,self).action_approve()

HrHolidays()