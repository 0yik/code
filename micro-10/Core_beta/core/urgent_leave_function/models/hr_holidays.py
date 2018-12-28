from odoo import api, fields, models
from odoo.exceptions import UserError

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    is_urgent = fields.Boolean(string='Urgent',track_visibility='onchange')
    report_note = fields.Text(string='HR Comments',track_visibility='onchange')

    @api.multi
    def action_approve(self):
        result = super(HrHolidays,self).action_approve()
        for holiday in self:
            if holiday.type == 'remove':
                if holiday.is_urgent != True:
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
            if holiday.is_urgent != False and holiday.holiday_status_id.limit == True:
                return result
        return result

HrHolidays()