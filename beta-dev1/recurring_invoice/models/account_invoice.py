# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class accoutn_invoice(models.Model):
    _inherit = 'account.invoice'

    recurrent = fields.Boolean('Recurrent', copy=False, default=False)
    interval_num = fields.Integer('Interval Number', copy=False)
    interval_unit = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'), ('months', 'Months'), ('years', 'Years')],
        'Interval Unit', default='days', copy=False)

    @api.model
    def _get_recurring_date(self):
        recurring_date = False
        date = fields.Datetime.from_string(self.date_invoice)
        unit = self.interval_unit
        interval = self.interval_num
        if unit == 'minutes':
            recurring_date = date + timedelta(minutes=interval)
        elif unit == 'hours':
            recurring_date = date + timedelta(hours=interval)
        elif unit == 'days':
            recurring_date = date + timedelta(days=interval)
        elif unit == 'months':
            recurring_date = self.get_recurring_date_month_year(months=True)
        elif unit == 'years':
            recurring_date = self.get_recurring_date_month_year(years=True)
        return recurring_date

    @api.model
    def get_recurring_date_month_year(self, months=False, years=False):
        date = fields.Datetime.from_string(self.date_invoice)
        year = date.year
        month = date.month
        day = date.day
        if months:
            year += int(month + self.interval_num) / 12
            month = int(month + self.interval_num) % 12
            if month == 0:
                month = 12
        if years:
            year += self.interval_num
        while True:
            try:
                date_string = '%s-%s-%s %s:%s:%s' % (year, month, day, date.hour, date.minute, date.second)
                return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            except:
                day -= 1
        return False

    @api.model
    def cron_recurring_invoice(self):
        invoice_ids = self.search(
            [('recurrent', '=', True), ('interval_num', '!=', False), ('interval_unit', '!=', False),
             ('date_invoice', '!=', False)])
        return invoice_ids._cron_recurring_invoice()

    @api.multi
    def _cron_recurring_invoice(self):
        now = datetime.now()
        for invoice in self:
            recurring_date = invoice._get_recurring_date()
            if recurring_date <= now:
                new_invoice = invoice.copy()
        return True
