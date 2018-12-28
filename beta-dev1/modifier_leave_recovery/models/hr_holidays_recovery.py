from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    is_recovery = fields.Boolean(string="Recovery Leave")
    supp_doc  = fields.Binary(string="Supporting document")

    @api.constrains('date_from','date_to')
    def _check_date(self):
        '''
        The method used to Validate leave request on same day.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current User Id
        @param ids : Current object Id
        @param context : Standard Dictionary
        @return : True or False
        ------------------------------------------------------
        '''
        for holiday in self:
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
                ('holiday_status_id.name', '!=', 'MOL'),
            ]

            domain2 = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('state', '=', 'validate'),
                ('id', '!=', holiday.id),
            ]
            ndholidays = self.search(domain2)

            diff_day = self._check_holiday_to_from_dates(holiday.date_from, holiday.date_to, holiday.employee_id.id)
            if self.is_recovery and self.half_day:
                diff_day = diff_day - 0.5

            for leave in ndholidays:
                if leave.number_of_days_temp < diff_day:
                    raise ValidationError(_('Sorry, you are trying to recover more days than your approved leave.'))

                if leave.date_to < holiday.date_to:
                    date_f = str(datetime.datetime.strptime(leave.date_from , DEFAULT_SERVER_DATETIME_FORMAT).date()) + " 00:00:00"
                    frm_date = datetime.datetime.strptime(date_f, DEFAULT_SERVER_DATETIME_FORMAT)
                    date_t = str(datetime.datetime.strptime(leave.date_to , DEFAULT_SERVER_DATETIME_FORMAT).date()) + " 00:00:00"
                    frm_to = datetime.datetime.strptime(date_t, DEFAULT_SERVER_DATETIME_FORMAT)
                    if leave.half_day:
                        if leave.am_or_pm == 'AM':
                            frm_date = frm_date + relativedelta(hour=8)
                            frm_to = frm_to + relativedelta(hour=12)
                        if leave.am_or_pm == 'PM':
                            frm_date = frm_date + relativedelta(hour=13)
                            frm_to = frm_to + relativedelta(hour=17)
                    else:
                        frm_date = frm_date + relativedelta(hour=8)
                        frm_to = frm_to + relativedelta(hour=17)
                    raise ValidationError(_('Employee does not have an approved leave request between %s and %s!') % ( frm_date , frm_to ))

            if not ndholidays and self.is_recovery:
                datesd = datetime.datetime.strptime((holiday.date_from).split(' ')[0],'%Y-%m-%d').strftime('%b %d %Y')
                datesf = datetime.datetime.strptime((holiday.date_to).split(' ')[0],'%Y-%m-%d').strftime('%b %d %Y')
                raise ValidationError(_('Employee does not have an approved leave request between %s and %s!') % ( datesd , datesf ))

#             raise ValidationError(_('test'))

            nholidays = self.search(domain)
            if nholidays and nholidays.ids:
                if holiday.type == 'add':
                    continue
                if holiday.half_day == True and holiday.type=='remove':
                    for new_holiday in nholidays:
                        if new_holiday.half_day == True:
                            if new_holiday.am_or_pm == holiday.am_or_pm:
                                raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))
                        else:
                            raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))
                else:
                    raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))
