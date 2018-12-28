from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

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

            date_from = str(datetime.datetime.strptime(holiday.date_from , DEFAULT_SERVER_DATETIME_FORMAT).date()) + " 00:00:00"
            date_to = str(datetime.datetime.strptime(holiday.date_to , DEFAULT_SERVER_DATETIME_FORMAT).date()) + " 23:59:59"
            domain2 = [
                ('date_from', '<=', date_to),
                ('date_to', '>=', date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('state', '=', 'validate'),
            ]
            ndholidays = self.search(domain2)
            if not ndholidays and self.is_recovery:
                datesd = datetime.datetime.strptime((holiday.date_from).split(' ')[0],'%Y-%m-%d').strftime('%b %d %Y')
                datesf = datetime.datetime.strptime((holiday.date_to).split(' ')[0],'%Y-%m-%d').strftime('%b %d %Y')
                raise ValidationError(_('Employee does not have an approved leave request between %s and %s!') % ( datesd , datesf ))

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
