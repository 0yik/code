from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

# 
#     is_urgent = fields.Boolean(string='Urgent')
#     report_note = fields.Text(string='HR Comments',track_visibility='onchange')
# 
#     @api.multi
#     def action_approve(self):
#         result = super(HrHolidays,self).action_approve()
#         for holiday in self:
#             if holiday.is_urgent != False and holiday.holiday_status_id.limit == True:
#                 return result
# 
# HrHolidays()
#     @api.onchange('holiday_status_id','urgent_leave')
#     def onchange_holiday_status(self):
#
#         for rec in self:
#             if rec.urgent_leave == True:
#                 if rec.holiday_status_id.name == 'Maternity Leave':
#                     raise UserError(_('%s is not eligible for Urgent Leave')% rec.holiday_status_id.name)

#     @api.constrains('state', 'number_of_days_temp', 'holiday_status_id')
#     def _check_holidays(self):
#         for holiday in self:
#             if holiday.holiday_type != 'employee' or holiday.type != 'remove' or not holiday.employee_id or holiday.holiday_status_id.limit:
#                 continue
#             leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
#             if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
#                             float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
#                 continue

    @api.model
    def create(self,values):
        res = super(HrHolidays, self).create(values)

        if self.is_urgent == True and self.type != 'add':

            urgent_leave_ids = self.env['leave.days.limit'].search([])

            # start_date = datetime.strptime(self.date_from, DEFAULT_SERVER_DATE_FORMAT)
            # two_days_ago_date = datetime.now() + timedelta(days=-2)
            # print "start_date",start_date
            # print "start_date",two_days_ago_date

            if self.holiday_status_id.name == 'ML':
                raise UserError(_('%s is not eligible for Urgent Leave')% self.holiday_status_id.name2)
            elif self.holiday_status_id.name == 'PL':
                raise UserError(_('%s is not eligible for Urgent Leave')% self.holiday_status_id.name2)
            elif self.holiday_status_id.name == 'SPL':
                raise UserError(_('%s is not eligible for Urgent Leave')% self.holiday_status_id.name2)
            elif self.holiday_status_id.name == 'OIL':
                raise UserError(_('%s is not eligible for Urgent Leave')% self.holiday_status_id.name2)
            else:
                return True
                # for urgent_leave_id in urgent_leave_ids:
                #     for leave_line in urgent_leave_id.leave_type_line_ids:
                #         if leave_line.leave_type_id.name == self.holiday_status_id.name:
                #             if self.number_of_days_temp <= urgent_leave_id.no_of_days:
                #                 todays_date = datetime.now()
                #                 date_from = datetime.strptime(self.date_from,
                #                                               DEFAULT_SERVER_DATETIME_FORMAT)
                #                 date_to = datetime.strptime(self.date_to,
                #                                             DEFAULT_SERVER_DATETIME_FORMAT)
                #
                #                 if date_from.date() < todays_date.date() and date_to.date() < todays_date.date():
                #                     return res
                #                 else:
                #                     raise UserError(
                #                         _(
                #                             '%s You can not select today or future date for urgent leave') % self.holiday_status_id.name)
                #             else:
                #                 raise UserError(
                #                     _('%s Urgent leave date limit only for %s days') % (
                #                     self.holiday_status_id.name, urgent_leave_id.no_of_days))
        return res
    
    @api.multi
    def write(self,values):
        res = super(HrHolidays, self).write(values)
        for rec in self:

            if rec.is_urgent == True and rec.type != 'add':

                urgent_leave_ids = self.env['leave.days.limit'].search([])

                if rec.holiday_status_id.name == 'ML':
                    raise UserError(_('%s is not eligible for Urgent Leave')% rec.holiday_status_id.name2)
                elif rec.holiday_status_id.name == 'PL':
                    raise UserError(_('%s is not eligible for Urgent Leave')% rec.holiday_status_id.name2)
                elif rec.holiday_status_id.name == 'SPL':
                    raise UserError(_('%s is not eligible for Urgent Leave')% rec.holiday_status_id.name2)
                elif rec.holiday_status_id.name == 'OIL':
                    raise UserError(_('%s is not eligible for Urgent Leave')% rec.holiday_status_id.name2)
                else:
                    return True
                    # for urgent_leave_id in urgent_leave_ids:
                    #     for leave_line in urgent_leave_id.leave_type_line_ids:
                    #         if leave_line.leave_type_id.name == self.holiday_status_id.name:
                    #             if self.number_of_days_temp <= urgent_leave_id.no_of_days:
                    #                 todays_date = datetime.now()
                    #                 date_from = datetime.strptime(self.date_from,
                    #                                                DEFAULT_SERVER_DATETIME_FORMAT)
                    #                 date_to = datetime.strptime(self.date_to,
                    #                                               DEFAULT_SERVER_DATETIME_FORMAT)
                    #
                    #                 if date_from.date() < todays_date.date() and date_to.date() < todays_date.date():
                    #                     return res
                    #                 else:
                    #                     raise UserError(
                    #                         _('%s You can not select today or future date for urgent leave') % rec.holiday_status_id.name)
                    #             else:
                    #                 raise UserError(
                    #                     _('%s Urgent leave date limit only for %s days') % (rec.holiday_status_id.name, urgent_leave_id.no_of_days))


        return res