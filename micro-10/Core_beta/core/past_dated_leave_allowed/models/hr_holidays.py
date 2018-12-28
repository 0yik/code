# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import datetime
from pytz import timezone
import pytz


class HolidaysType(models.Model):
    _inherit = 'hr.holidays.status'

    allow_past_date = fields.Boolean(
        string='Past Dated',
        help='Tick if you want to allow apply leave for past date.')
    allow_past_days = fields.Integer(
        string='Past Dated Days',
        help='Add days which you want to allow for \
        past days from today\'s date.')

    #  @api.onchange('allow_past_date')
    #  def onchage_allow_past_date(self):
    #      """docstring for onchage_allow_past_date"""
    #      if not self.allow_past_date:
    #          self.allow_past_days = 0


HolidaysType()


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.constrains('date_from')
    def _check_past_date(self):
        for obj in self:
            # if not obj.holiday_status_id.allow_past_date and fields.Datetime.from_string(obj.date_from) < fields.Datetime.from_string(fields.Datetime.now()).replace(hour=00,minute=00,second=01):
            #     #fields.Datetime.now():
            #     tz = pytz.timezone(self.env.user.tz)
            #     # print "JJJJJJJ", fields.Datetime.context_timestamp(self.with_context(tz=tz), datetime.datetime.now())
            #     raise ValidationError(
            #         _("Past date not allowed. Please select date that is %s onwards." % (
            #             datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S'))))
            if obj.holiday_status_id.allow_past_date:
                allowed_past_date = datetime.date.today() - datetime.timedelta(days=obj.holiday_status_id.allow_past_days)
                if datetime.datetime.strptime(obj.date_from,'%Y-%m-%d %H:%M:%S').date() < allowed_past_date:
                    raise ValidationError(
                    _("Past date not allowed. Please select date that is %s onwards." % (
                        allowed_past_date.strftime('%d/%m/%Y'))))
