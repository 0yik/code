# -*- coding: utf-8 -*-

from __future__ import division
from odoo import models, fields, api, _
import time
import pytz
from datetime import date, datetime, timedelta, time, date
import calendar
from odoo.exceptions import UserError, ValidationError, Warning
from unittest2.test.test_program import RESULT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from mako.pyparser import reserved


class reschedule_booking(models.TransientModel):
    
    _name = 'reschedule.booking'
    
    start_date = fields.Date("Start Date", required="1")
    start_time = fields.Float('Start Time',required="1")
    end_date = fields.Date("End Date",required="1")
    end_time = fields.Float('End Time',required="1")
    booking_type = fields.Char('booking type')
    
    @api.multi
    def reschedule_booking(self):
        if self.start_time > 24.0 or self.end_time > 24.0:
            raise Warning(_("Please select proper time."))
        booking_id = self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id'))
        if booking_id and booking_id.booking_type == 'special':
            # 2017-11-22 14.75 2017-11-22 15.75 [u'1.5', u'2'] [[u'5', u'1'], [u'4', u'2']] 3 no 398670
            total_hours = []
            all_anchors = []
            if booking_id.project_booking_anchor_ids:
                for an in booking_id.project_booking_anchor_ids:
                    type_an = self.env['anchor.master'].search([('anchor_type_id','=', an.anchor_type_id and an.anchor_type_id.id)])
                    if an.an_complexity == 'complex':
                        total_hours.append(str(float(type_an.complex_time) * float(an.anchor_qty)).decode('utf-8'))
                    if an.an_complexity == 'simple':
                        total_hours.append(str(float(type_an.simple_time) * float(an.anchor_qty)).decode('utf-8'))
                    if an.an_complexity == 'medium':
                        total_hours.append(str(float(type_an.medium_time) * float(an.anchor_qty)).decode('utf-8'))
                    all_anchors.append([str(an.anchor_size_id.id).decode('utf-8'),str(an.anchor_type_id.id).decode('utf-8')])
            if booking_id.sid_required == False:
                sic = 'no'
            else:
                sic = 'yes'
            booking_logic = self.env[self._context.get('active_model')].sudo().dedicated_booking_logic(self.start_date,self.start_time,self.end_date,self.end_time,total_hours, all_anchors, booking_id.project_id.id, sic, booking_id.postal_code.name)
            if booking_logic == False:
                raise Warning(_("Testers are not available for the booking on (selected date time).Please select another date and time for your booking. Sorry for the inconvenience. Thank You."))
            else:
                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
                l_start_time = "%02d:%02d:%02d" % (int(self.start_time), (self.start_time*60) % 60, (self.start_time*3600) % 60)
                l_end_time = "%02d:%02d:%02d" % (int(self.end_time), (self.end_time*60) % 60, (self.end_time*3600) % 60)
                booking_start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d").date()
                booking_end_date = datetime.strptime(str(self.end_date), "%Y-%m-%d").date()
                dt_start = datetime.combine(booking_start_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
                dt_end = datetime.combine(booking_end_date, datetime.strptime(l_end_time, "%H:%M:%S").time())
                local = pytz.timezone(self._context.get('tz'))
                check_dt_start = datetime.strptime(str(dt_start), "%Y-%m-%d %H:%M:%S") 
                check_dt_end = datetime.strptime(str(dt_end), "%Y-%m-%d %H:%M:%S")
                dt_start = local.localize(check_dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_end = local.localize(check_dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id')).write({'start_date_time': dt_start,
                                                                                                                 'end_date_time': dt_end,
                                                                                                                 'user_tester_id': tester_id and tester_id.id,
                                                                                                                 'status': 'rescheduled'})
        if booking_id and booking_id.booking_type == 'sic':
            # 2017-12-08 13.00 15.50 398670
            booking_logic = self.env[self._context.get('active_model')].sudo().sic_booking_logic(self.start_date,self.start_time,self.end_time,booking_id.postal_code.name)
            if booking_logic == False:
                raise Warning(_("Testers are not available for the booking on (selected date time).Please select another date and time for your booking. Sorry for the inconvenience. Thank You."))
            else:
                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
                booking_id.tester_id.project_ids = [(3, booking_id.project_id.id)]
                tester_id.partner_id.project_ids = [(4, booking_id.project_id.id)]
                l_start_time = "%02d:%02d:%02d" % (int(self.start_time), (self.start_time*60) % 60, (self.start_time*3600) % 60)
                l_end_time = "%02d:%02d:%02d" % (int(self.end_time), (self.end_time*60) % 60, (self.end_time*3600) % 60)
                booking_start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d").date()
                dt_start = datetime.combine(booking_start_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
                dt_end = datetime.combine(booking_start_date, datetime.strptime(l_end_time, "%H:%M:%S").time())
                local = pytz.timezone(self._context.get('tz'))
                check_dt_start = datetime.strptime(str(dt_start), "%Y-%m-%d %H:%M:%S") 
                check_dt_end = datetime.strptime(str(dt_end), "%Y-%m-%d %H:%M:%S")
                dt_start = local.localize(check_dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_end = local.localize(check_dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                self.env[self._context.get('active_model')].sudo().browse(self._context.get('active_id')).write({'start_date_time': dt_start,
                                                                                                                 'end_date_time': dt_end,
                                                                                                                 'user_tester_id': tester_id and tester_id.id,
                                                                                                                 'status': 'rescheduled'})
        return True
    