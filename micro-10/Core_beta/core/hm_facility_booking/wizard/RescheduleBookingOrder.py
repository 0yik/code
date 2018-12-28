# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

class report_account_wizard(models.TransientModel):
    _name = "booking.reschedule.wizard"

    current_start_date = fields.Datetime('Current Booking Start Date', readonly=True)
    current_end_date = fields.Datetime('Current Booking End Date', readonly=True)
    new_start_date = fields.Datetime('New Booking Start Date')
    new_end_date = fields.Datetime('New Booking Start Date')

    @api.model
    def default_get(self, fields_list):
        res = super(report_account_wizard, self).default_get(fields_list)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id') or []
        for record in self.env[active_model].browse(active_id):
            res['current_start_date'] = record.booking_start_date
            res['current_end_date'] = record.booking_end_date
            return res

    def reschedule_confirm(self):
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id') or []
        for record in self.env[active_model].browse(active_id):
            check_overlapped = record.check_overlapped_booking(record.facility_id.id,self.new_start_date, self.new_end_date)
            if check_overlapped:
                mess = "This Facility has already been booked from %s to %s" % (
                    datetime.strptime(record.booking_start_date, DEFAULT_SERVER_DATETIME_FORMAT).strftime(
                        '%d/%m/%Y %I:%M:%S'),
                    datetime.strptime(record.booking_end_date,
                                      DEFAULT_SERVER_DATETIME_FORMAT).strftime(
                        '%d/%m/%Y %I:%M:%S')
                )
                raise UserError(_(mess))
            else:
                record.booking_start_date = self.new_start_date
                record.booking_end_date = self.new_end_date