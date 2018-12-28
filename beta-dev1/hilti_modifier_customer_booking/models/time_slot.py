# -*- coding: utf-8 -*-

from __future__ import division
from odoo import models, fields, api, _
from lxml import etree
import time
import json
import pytz
from datetime import date, datetime, timedelta, time, date
import calendar
from odoo.exceptions import UserError, ValidationError, Warning
from unittest2.test.test_program import RESULT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from mako.pyparser import reserved
# from ldif import start_time

def get_daily_slots(start, end, slot, date, lunch_start, lunch_end):
    dt = datetime.combine(date, datetime.strptime(start, "%H:%M:%S").time())
    lunch_start = datetime.combine(date, datetime.strptime(lunch_start,"%H:%M:%S").time())
    lunch_end = datetime.combine(date, datetime.strptime(lunch_end,"%H:%M:%S").time())
    slots = []
    while (dt.time() < datetime.strptime(end, "%H:%M:%S").time()):
        sl = [dt.strftime('%H:%M')]
        dt = dt + timedelta(minutes=slot)
        sl.append(dt.strftime('%H:%M'))
        if (lunch_start < dt <= lunch_end):
            continue
        else:
            slots.append(sl)
    return slots

def remove_none(vals):
    for k,v in vals.items(): 
        if vals[k] is None:
            vals[k] = False
    return vals
    
class time_slot_start(models.Model):
    _name = 'time.slot.start'
    _rec_name = 'start_time'

    start_time = fields.Float('Start Time')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%d:%02d" % (int(record.start_time), (record.start_time * 60) % 60)
            res.append((record.id, name))
        return res


class time_slot_end(models.Model):
    _name = 'time.slot.end'
    _rec_name = 'end_time'

    end_time = fields.Float('End Time')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = "%d:%02d" % (int(record.end_time), (record.end_time * 60) % 60)
            res.append((record.id, name))
        return res


class time_slot_start_end(models.Model):
    _name = 'time.slot.start.end'
    _rec_name = "timeslot_start_id"

    @api.multi
    def name_get(self):
        res = []
        if 'display_start_time' in self._context:
            return super(time_slot_start_end, self).name_get()
        else:
            for record in self:
                sp_name_co = "%d:%02d" % (int(record.timeslot_start_id.start_time), (record.timeslot_start_id.start_time * 60) % 60)
                sn_name_co = "%d:%02d" % (int(record.timeslot_end_id.end_time), (record.timeslot_end_id.end_time * 60) % 60)
                name = ''.join([str(sp_name_co) , ' - ', str(sn_name_co)])
                res.append((record.id, name))
            return res

    sequence = fields.Integer(default=10)
    timeslot_start_id = fields.Many2one('time.slot.start', string="Start Time")
    timeslot_end_id = fields.Many2one('time.slot.end', string="End Time")
    start = fields.Float(related="timeslot_start_id.start_time", string="Start Time")
    end = fields.Float(related="timeslot_end_id.end_time", string="End Time")
    time_master_id = fields.Many2one('timeslot.master', string="End Time")


class time_slot_master(models.Model):
    _name = 'timeslot.master'
    _description = "Timeslot Management"

    name = fields.Char(string="Name")
    time_slot_based = fields.Boolean('Dynamic Timeslots - Based on the time required per anchor')
    start_time = fields.Float("Start Time")
    end_time = fields.Float("End Time")
    segment_time = fields.Integer("Segment Time")
    lunch_start_time = fields.Float("Lunch Start Time (HH:MM)")
    lunch_end_time = fields.Float("Lunch End Time (HH:MM)")
    calandar_display = fields.Integer('Display calendar months')
    time_slot_ids = fields.One2many('time.slot.start.end', 'time_master_id', string="Time Slot")

    def timeslot_calculation(self, vals):
        import time
        self.env['time.slot.start.end'].search([('time_master_id', '=', self.id)]).unlink()
        start_time = vals.get('start_time') or self.start_time
        end_time = vals.get('end_time') or self.end_time
        slot_time = vals.get('segment_time') or self.segment_time
        lunch_start_time = vals.get('lunch_start_time') or self.lunch_start_time
        lunch_end_time = vals.get('lunch_end_time') or self.lunch_end_time
        l_start_time = "%d:%02d:%02d" % (int(lunch_start_time), (lunch_start_time*60) % 60, (lunch_start_time*3600) % 60)
        l_end_time = "%d:%02d:%02d" % (int(lunch_end_time), (lunch_end_time*60) % 60, (lunch_end_time*3600) % 60)
        slots = get_daily_slots(start="%d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60), end="%d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60), slot=slot_time, date=datetime.now().date(), lunch_start=l_start_time, lunch_end=l_end_time)
        for slot in slots:
            self.env['time.slot.start.end'].create({
                'timeslot_start_id': self.env['time.slot.start'].create({
                     'start_time': time.strptime(slot[0], "%H:%M").tm_hour + int(time.strptime(slot[0], "%H:%M").tm_min) / 60
                }).id,
                'timeslot_end_id': self.env['time.slot.end'].create({
                    'end_time': time.strptime(slot[1], "%H:%M").tm_hour + int(time.strptime(slot[1], "%H:%M").tm_min) / 60
                }).id,
                'time_master_id': self.id
            })
        return True

    @api.multi
    def write(self, vals):
        if ('start_time' in vals and vals.get('start_time') > 0.00) or ('end_time' in vals and vals.get('end_time') > 0.00) or ('segment_time' in vals and vals.get('segment_time') > 0):
            for rec in self:
                rec.timeslot_calculation(vals)
        else:
            vals.update({
                'start_time': 0.0,
                'end_time': 0.0,
                'segment_time': 0,
            })
        if 'time_slot_based' in vals and vals.get('time_slot_based') == False:
            for rec in self:
                rec.time_slot_ids.unlink()
        return super(time_slot_master, self).write(vals)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('timeslot.master') or _('New')
        get_all_record = self.search_count([])
        if get_all_record >= 1:
            raise Warning(_("Timeslot Management already exist."))
        result = super(time_slot_master, self).create(vals)
        if ('start_time' in vals) or ('end_time' in vals) or ('segment_time' in vals):
            result.timeslot_calculation(vals)
        return result


class timeslot_booking(models.Model):
    _name = 'timeslot.booking'

    booking_date = fields.Date('Booking Date')
    time_slot_id = fields.Many2one('time.slot.start.end', string="Start and End Time")
    timeslot_start_id = fields.Many2one(related="time_slot_id.timeslot_start_id", string="Start Time")
    timeslot_end_id = fields.Many2one(related="time_slot_id.timeslot_end_id", string="End Time")
    start = fields.Float(related="timeslot_start_id.start_time", string="Start Time")
    end = fields.Float(related="timeslot_end_id.end_time", string="End Time")
    user_id = fields.Many2one('res.users', string="User")
    tester_id = fields.Many2one('res.users')
    pr_booking_id = fields.Many2one('project.booking', string="Project Booking")
    temp = fields.Boolean(string="Temp")


    def get_rebook_booking_slot(self,booking_date, postal_code, project_id, booking_anchor_ids, sid_required, total_hours):
        local = pytz.timezone(self.env.user.tz)
        all_anchors = []
        if booking_anchor_ids and booking_anchor_ids[0] != 'sic_booking':
            total_hours = []
            for an in booking_anchor_ids[0]:
                type_an = self.env['anchor.master'].search([('anchor_type_id','=', an[2]['anchor_type_id'])])
                if an[2]['an_complexity'] == 'complex':
                    total_hours.append(str(float(type_an.complex_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                if an[2]['an_complexity'] == 'simple':
                    total_hours.append(str(float(type_an.simple_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                if an[2]['an_complexity'] == 'medium':
                    total_hours.append(str(float(type_an.medium_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                all_anchors.append([str(an[2]['anchor_size_id']).decode('utf-8'),str(an[2]['anchor_type_id']).decode('utf-8')])
        if booking_anchor_ids and booking_anchor_ids[0] == 'sic_booking':
            all_anchors.append(booking_anchor_ids[0])
        if sid_required == False:
            sic = 'no'
        else:
            sic = 'yes'
        postal_code = self.env['postal.code'].search([('id', '=', postal_code)])
        if postal_code:
            postal_code = postal_code.name
        time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
        slot_time = False
        if not time_slot.time_slot_based:
            booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, slot_time)
            def call_booking_order_static(booking_logic):
                booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
#                         booking_logic = call_booking_order(booking_logic)
                return booking_logic
            if type(booking_logic) == list:
                if booking_logic and booking_logic[0] != False:
                    booking_logic = call_booking_order_static(booking_logic)
            remaining_slot = []
            if type(booking_logic) != list and type(booking_logic) == dict:
                for slot_book in booking_logic.keys():
                    if type(booking_logic[slot_book]) != list:
                        slot_book_value = [booking_logic[slot_book]]
                    else:
                        slot_book_value = booking_logic[slot_book]
                    remaining_slot.extend(slot_book_value)
            if remaining_slot:
                return {'domain': {'time_slot_id': [('id', 'in', remaining_slot)]}}
            else:
                return {'domain': {'time_slot_id': [('id', 'in', [])]}}
        else:
            remaining_slot = []
            booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, slot_time)
            def call_booking_order(booking_logic):
                booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
#                         booking_logic = call_booking_order(booking_logic)
                return booking_logic
            if type(booking_logic) == list:
                if booking_logic and booking_logic[0] != False:
                    booking_logic = call_booking_order(booking_logic)
            if type(booking_logic) != list and type(booking_logic) == dict:
                for slot_book in booking_logic.keys():
                    slot_book_value = []
                    for aa in booking_logic[slot_book]:
                        if type(aa) != list:
                            slot_book_value.append(booking_logic[slot_book])
                            break
                        else:
                            slot_book_value = booking_logic[slot_book]
                            break
                    for time1 in slot_book_value:
                        all_time = self.env['time.slot.start.end'].sudo().search([])
                        for aa in all_time:
                            if aa.timeslot_start_id.start_time == time1[0]:
                                remaining_slot.append(aa.id)
            if remaining_slot:
                return {'domain': {'time_slot_id': [('id', 'in', remaining_slot)]}}
            else:
                return {'domain': {'time_slot_id': [('id', 'in', [])]}}

    def get_reschedule_booking_slot(self, booking_date, project_booking_id):

        pb_id = self.env['project.booking'].search([('id', '=', project_booking_id)])
        final_time_id = []
        return_list = []
        time_slot_based = ''
        if booking_date:
            start_date_day_name = datetime.strftime(datetime.strptime(booking_date, DEFAULT_SERVER_DATE_FORMAT), '%A')

            if (start_date_day_name in ["Sunday", "Saturday"]) and pb_id.booking_type not in ['special']:
                raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))

            start_date = datetime.strftime(datetime.strptime(booking_date, DEFAULT_SERVER_DATE_FORMAT), "%Y-%m-%d")
            holidays = self.env['holiday.holiday'].search([('holiday_date', '=', start_date)])
            if holidays and pb_id.booking_type not in ['special']:
                raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))
        slot_time = False
        total_hours = []
        all_anchors = []
        if pb_id.booking_type == 'sic':
            all_anchors = ['sic_booking']
            total_hours.append(str(float(pb_id.sic_required_hours)).decode('utf-8'))
        for an in pb_id.project_booking_anchor_ids:
            type_an = self.env['anchor.master'].search([('anchor_type_id','=', an.anchor_type_id and an.anchor_type_id.id)])
            if an.an_complexity == 'complex':
                total_hours.append(str(float(type_an.complex_time) * float(an.anchor_qty)).decode('utf-8'))
            if an.an_complexity == 'simple':
                total_hours.append(str(float(type_an.simple_time) * float(an.anchor_qty)).decode('utf-8'))
            if an.an_complexity == 'medium':
                total_hours.append(str(float(type_an.medium_time) * float(an.anchor_qty)).decode('utf-8'))
            all_anchors.append([str(an.anchor_size_id.id).decode('utf-8'),str(an.anchor_type_id.id).decode('utf-8')])
        if pb_id.sid_required == False:
            sic = 'no'
        else:
            sic = 'yes'
        # 2017-11-30 [u'1.5', u'2'] [[u'6', u'1'], [u'5', u'2']] 3 yes 398670 False
        if booking_date:
            if 'calling_from_app' not in self._context:
                self.time_slot_id = False
            time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
            if not time_slot.time_slot_based:
                time_slot_based = 'static'
                booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, slot_time)
                def call_booking_order_static(booking_logic):
                    booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order_static(booking_logic)
                remaining_slot = []
                if type(booking_logic) != list and type(booking_logic) == dict:
                    for slot_book in booking_logic.keys():
                        if type(booking_logic[slot_book]) != list:
                            slot_book_value = [booking_logic[slot_book]]
                        else:
                            slot_book_value = booking_logic[slot_book]
                        if self._context and 'calling_from_app' in self._context:
                            for time in slot_book_value:
                                time = self.env['time.slot.start.end'].sudo().browse([time])
                                start = int(time.timeslot_start_id.start_time)
                                end = int(time.timeslot_end_id.end_time)

                                start_time = "%02d:%02d" % (int(time.timeslot_start_id.start_time), (time.timeslot_start_id.start_time * 60) % 60)
                                end_time = "%02d:%02d" % (int(time.timeslot_end_id.end_time), (time.timeslot_end_id.end_time * 60) % 60)
                                if start > 12:
                                    start = (start - 12)
                                    start_time = "%02d:%02d" % ((int(time.timeslot_start_id.start_time) - 12), (time.timeslot_start_id.start_time * 60) % 60)
                                if end > 12:
                                    end = (end - 12)
                                    end_time = "%02d:%02d" % ((int(time.timeslot_end_id.end_time) - 12), (time.timeslot_end_id.end_time * 60) % 60)
            #                     if time.id in booking_time_ids:
                                final_time_id.append({'start':time.timeslot_start_id.start_time,
                                                      'start_time':  start_time,
                                                      'time_slot_id': time.id,
                                                      'tester_id': slot_book,
                                                      'end':time.timeslot_end_id.end_time,
                                                      'end_time':  end_time, })
                        else:
                            remaining_slot.extend(slot_book_value)
            else:
                time_slot_based = 'dynamic'
                if 'calling_from_app' not in self._context:
                    self.time_slot_id = False
                remaining_slot = []
                booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, slot_time)
                def call_booking_order(booking_logic):
                    booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order(booking_logic)
                if type(booking_logic) != list and type(booking_logic) == dict:
                    for slot_book in booking_logic.keys():
                        slot_book_value = []
                        for aa in booking_logic[slot_book]:
                            if type(aa) != list:
                                slot_book_value.append(booking_logic[slot_book])
                                break
                            else:
                                slot_book_value = booking_logic[slot_book]
                                break
                        for time1 in slot_book_value:
                            if self._context and 'calling_from_app' in self._context:
                                all_time = self.env['time.slot.start.end'].sudo().search([])
                                time_slot_id = []
                                time = False
                                for aa in all_time:
                                    if aa.timeslot_start_id.start_time == time1[0]:
                                        time = aa
                                        time_slot_id.append(aa.id)
                                    if aa.timeslot_start_id.start_time > time1[0] and aa.timeslot_end_id.end_time < time1[1]:
                                        time_slot_id.append(aa.id)
                                    if aa.timeslot_end_id.end_time == time1[1]:
                                        time_slot_id.append(aa.id)
                                start = int(time.timeslot_start_id.start_time)
                                end = int(time.timeslot_end_id.end_time)
                                start_time = "%02d:%02d" % (int(time.timeslot_start_id.start_time), (time.timeslot_start_id.start_time * 60) % 60)
                                end_time = "%02d:%02d" % (int(time.timeslot_end_id.end_time), (time.timeslot_end_id.end_time * 60) % 60)
                                if start > 12:
                                    start = (start - 12)
                                    start_time = "%02d:%02d" % ((int(time.timeslot_start_id.start_time) - 12), (time.timeslot_start_id.start_time * 60) % 60)
                                if end > 12:
                                    end = (end - 12)
                                    end_time = "%02d:%02d" % ((int(time.timeslot_end_id.end_time) - 12), (time.timeslot_end_id.end_time * 60) % 60)
            #                     if time.id in booking_time_ids:
                                final_time_id.append({'start':time.timeslot_start_id.start_time,
                                                      'start_time':  start_time,
                                                      'time_slot_id': time_slot_id,
                                                      'tester_id': slot_book,
                                                      'end':time.timeslot_end_id.end_time,
                                                      'end_time':  end_time, })
                            else:
                                all_time = self.env['time.slot.start.end'].sudo().search([])
                                for aa in all_time:
                                    if aa.timeslot_start_id.start_time == time1[0]:
                                        remaining_slot.append(aa.id)
            if self._context and 'calling_from_app' in self._context:
                return_list.append(final_time_id)
                return_list.append(booking_date)
                return_list.append(time_slot_based)
                return return_list
            else:
                if remaining_slot:
                    return {'domain': {'time_slot_id': [('id', 'in', remaining_slot)]}}
                else:
                    return {'domain': {'time_slot_id': [('id', 'in', [])]}}


    @api.onchange('booking_date')
    def onchange_booking_date(self):
        if 'parent_postal_code' and 'parent_project_id' in self._context and self.booking_date:
            total_hours = []
            all_anchor = []
            if 'parent_booking_type' in self._context and 'parent_sic_required_hours' in self._context and self._context['parent_booking_type'] == 'sic':
                total_hours.append(str(float(self._context['parent_sic_required_hours'])).decode('utf-8'))
                all_anchor = ['sic_booking']
            else:
                all_anchor.append(self._context.get('parent_project_booking_anchor_ids'))
            get_slot = self.get_rebook_booking_slot(self.booking_date, self._context.get('parent_postal_code'), self._context.get('parent_project_id'), all_anchor, self._context.get('parent_sid_required'), total_hours)
            return get_slot
        if self._context.get('default_pr_booking_id'):
            get_re_slot = self.get_reschedule_booking_slot(self.booking_date, self._context.get('default_pr_booking_id'))
            return get_re_slot
        if not self.booking_date:
            return {'domain': {'time_slot_id': []}}


    def get_tester_from_create(self, pr_booking_id, booking_date, vals_time_slot_id, anchor_ids):
        new_create_list = []
        tester_id = False
        pb_id = self.env['project.booking'].search([('id', '=', pr_booking_id)])
        if pb_id:
            slot_time = False
            total_hours = []
            all_anchors = []
            if anchor_ids and anchor_ids[0] != 'sic_booking':
                for an in anchor_ids:
                    type_an = self.env['anchor.master'].search([('anchor_type_id','=', an[2]['anchor_type_id'])])
                    if an[2]['an_complexity'] == 'complex':
                        total_hours.append(str(float(type_an.complex_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                    if an[2]['an_complexity'] == 'simple':
                        total_hours.append(str(float(type_an.simple_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                    if an[2]['an_complexity'] == 'medium':
                        total_hours.append(str(float(type_an.medium_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                    all_anchors.append([str(an[2]['anchor_size_id']).decode('utf-8'),str(an[2]['anchor_type_id']).decode('utf-8')])
            else:
                total_hours.append(str(float(pb_id.sic_required_hours)).decode('utf-8'))
            if pb_id.sid_required == False:
                sic = 'no'
            else:
                sic = 'yes'
            # 2017-11-30 [u'1.5', u'2'] [[u'6', u'1'], [u'5', u'2']] 3 yes 398670 False
            time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
            if not time_slot.time_slot_based:
                booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, slot_time)
                def call_booking_order_static_create(booking_logic):
                    booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.env['project.booking'].sudo().booking_logic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order_static_create(booking_logic)
                if booking_logic and vals_time_slot_id:
                    if type(booking_logic) != list and type(booking_logic) == dict:
                        for slot_book in booking_logic.keys():
                            if type(booking_logic[slot_book]) != list:
                                slot_book_value = [booking_logic[slot_book]]
                            else:
                                slot_book_value = booking_logic[slot_book]
                            if vals_time_slot_id in slot_book_value:
                                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', slot_book)])
                                if tester_id and tester_id.id:
                                    tester_id = tester_id.id

                                #pb_id.user_tester_id = tester_id and tester_id.id or False
                return [False, tester_id]
            else:
                booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, slot_time)
                def call_booking_order(booking_logic):
                    booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order(booking_logic)
                final_time_id = []
                return_list = []
                if type(booking_logic) != list and type(booking_logic) == dict:
                    time_slot_id = []
                    for slot_book in booking_logic.keys():
                        slot_book_value = []
                        for aa in booking_logic[slot_book]:
                            if type(aa) != list:
                                slot_book_value.append(booking_logic[slot_book])
                                break
                            else:
                                slot_book_value = booking_logic[slot_book]
                                break
                        for time1 in slot_book_value:
                            all_time = self.env['time.slot.start.end'].sudo().search([])
                            book_id = self.env['time.slot.start.end'].sudo().search([('id', '=', vals_time_slot_id)])
                            if book_id.timeslot_start_id.start_time == time1[0]:
                                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', slot_book)])
                                if tester_id and tester_id.id:
                                    tester_id = tester_id.id
                                #pb_id.user_tester_id = tester_id and tester_id.id or False
                                for aa in all_time:
                                    if aa.timeslot_start_id.start_time == time1[0]:
                                        time = aa
                                        time_slot_id.append(aa.id)
                                    if aa.timeslot_start_id.start_time > time1[0] and aa.timeslot_end_id.end_time < time1[1]:
                                        time_slot_id.append(aa.id)
                                    if aa.timeslot_end_id.end_time == time1[1]:
                                        time_slot_id.append(aa.id)
                    time_slot_id.remove(vals_time_slot_id)
                    for slot in time_slot_id:
                        new_create_list.append({'booking_date': booking_date, 'time_slot_id': slot, 'pr_booking_id': pb_id and pb_id.id or False})
                return [new_create_list, tester_id]

    @api.model
    def create(self, vals):
        new_create_list = []
        pb_existing_id = False
        assign_tester_id = False
        tester_id_from_function = False
        all_anchor = []
        if vals and 'pr_booking_id' in vals.keys() and 'call_super' not in self._context:
            pb_existing_id = self.env['project.booking'].search([('id', '=', vals.get('pr_booking_id'))])
            if pb_existing_id and pb_existing_id.booking_type == 'sic':
                all_anchor = ['sic_booking']
            else:
                all_anchor = self._context.get('parent_create_anchor_ids')
            new_create_list_result = self.get_tester_from_create(vals['pr_booking_id'],vals['booking_date'], vals['time_slot_id'], all_anchor)
            if not new_create_list_result[1]:
                raise Warning(_("Testers are not available for the booking on (selected date time).Please select another date and time for your booking. Sorry for the inconvenience. Thank You."))
            new_create_list = new_create_list_result[0]
            tester_id_from_function = new_create_list_result[1]

        if 'is_reschedule' in self._context and self._context.get('is_reschedule') and 'call_super' not in self._context:
            pb_id = self.env['project.booking'].search([('id', '=', self._context.get('default_pr_booking_id'))])
            if vals.get('booking_date'):
                start_date_day_name = datetime.strftime(datetime.strptime(vals.get('booking_date'), DEFAULT_SERVER_DATE_FORMAT), '%A')

                if (start_date_day_name in ["Sunday", "Saturday"]) and pb_id.booking_type not in ['special']:
                    raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))

                start_date = datetime.strftime(datetime.strptime(vals.get('booking_date'), DEFAULT_SERVER_DATE_FORMAT), "%Y-%m-%d")
                holidays = self.env['holiday.holiday'].search([('holiday_date', '=', start_date)])
                if holidays and pb_id.booking_type not in ['special']:
                    raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))
            slot_time = False
            total_hours = []
            all_anchors = []
            if self._context.get('pr_booking_type_reschedule') and self._context['pr_booking_type_reschedule'] == 'sic':
                all_anchors = ['sic_booking']
                total_hours.append(str(float(pb_id.sic_required_hours)).decode('utf-8'))
            else:
                for an in pb_id.project_booking_anchor_ids:
                    type_an = self.env['anchor.master'].search([('anchor_type_id','=', an.anchor_type_id and an.anchor_type_id.id)])
                    if an.an_complexity == 'complex':
                        total_hours.append(str(float(type_an.complex_time) * float(an.anchor_qty)).decode('utf-8'))
                    if an.an_complexity == 'simple':
                        total_hours.append(str(float(type_an.simple_time) * float(an.anchor_qty)).decode('utf-8'))
                    if an.an_complexity == 'medium':
                        total_hours.append(str(float(type_an.medium_time) * float(an.anchor_qty)).decode('utf-8'))
                    all_anchors.append([str(an.anchor_size_id.id).decode('utf-8'),str(an.anchor_type_id.id).decode('utf-8')])
            if pb_id.sid_required == False:
                sic = 'no'
            else:
                sic = 'yes'
            # 2017-11-30 [u'1.5', u'2'] [[u'6', u'1'], [u'5', u'2']] 3 yes 398670 False
            time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
            if not time_slot.time_slot_based:
                booking_logic = self.env['project.booking'].sudo().booking_logic(vals['booking_date'],total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, slot_time)
                def call_booking_order_static_create(booking_logic):
                    booking_logic = self.env['project.booking'].sudo().booking_logic(vals['booking_date'],total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.env['project.booking'].sudo().booking_logic(vals['booking_date'],total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order_static_create(booking_logic)
                if booking_logic and vals and 'time_slot_id' in vals.keys():
                    if type(booking_logic) != list and type(booking_logic) == dict:
                        for slot_book in booking_logic.keys():
                            if type(booking_logic[slot_book]) != list:
                                slot_book_value = [booking_logic[slot_book]]
                            else:
                                slot_book_value = booking_logic[slot_book]
                            if vals['time_slot_id'] in slot_book_value:
                                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', slot_book)])
                                assign_tester_id = tester_id and tester_id.id or False
                                #pb_id.user_tester_id = tester_id and tester_id.id or False
            else:
                booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(vals['booking_date'],total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, slot_time)
                def call_booking_order(booking_logic):
                    booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(vals['booking_date'],total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.env['project.booking'].sudo().booking_logic_dynamic(vals['booking_date'],total_hours, all_anchors, pb_id.project_id.id, sic, pb_id.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order(booking_logic)
                final_time_id = []
                return_list = []
                if type(booking_logic) != list and type(booking_logic) == dict:
                    time_slot_id = []
                    for slot_book in booking_logic.keys():
                        slot_book_value = []
                        for aa in booking_logic[slot_book]:
                            if type(aa) != list:
                                slot_book_value.append(booking_logic[slot_book])
                                break
                            else:
                                slot_book_value = booking_logic[slot_book]
                                break
                        for time1 in slot_book_value:
                            all_time = self.env['time.slot.start.end'].sudo().search([])
                            book_id = self.env['time.slot.start.end'].sudo().search([('id', '=', vals['time_slot_id'])])
                            if book_id.timeslot_start_id.start_time == time1[0]:
                                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', slot_book)])
                                pb_id.user_tester_id = tester_id and tester_id.id or False
                                for aa in all_time:
                                    if aa.timeslot_start_id.start_time == time1[0]:
                                        time = aa
                                        time_slot_id.append(aa.id)
                                    if aa.timeslot_start_id.start_time > time1[0] and aa.timeslot_end_id.end_time < time1[1]:
                                        time_slot_id.append(aa.id)
                                    if aa.timeslot_end_id.end_time == time1[1]:
                                        time_slot_id.append(aa.id)
                    time_slot_id.remove(vals['time_slot_id'])
                    for slot in time_slot_id:
                        new_create_list.append({'booking_date': vals['booking_date'], 'time_slot_id': slot, 'pr_booking_id': pb_id and pb_id.id or False})
            old_booking_rec = self.search([('pr_booking_id', '=', self._context.get('default_pr_booking_id'))])
            if old_booking_rec:
                for an in old_booking_rec:
                    an.unlink()
        res = super(timeslot_booking, self).create(vals)
        pb_last_id = self.env['project.booking'].search([('id', '=', self._context.get('default_pr_booking_id'))])
        if new_create_list and (pb_last_id or pb_existing_id):
            for a in new_create_list:
                self.with_context({'call_super': True}).create(a)
        if tester_id_from_function and pb_existing_id:
            pb_existing_id.user_tester_id = tester_id_from_function
        if assign_tester_id:
            pb_last_id.user_tester_id = assign_tester_id
        return res

class holiday(models.Model):
    _name = 'holiday.holiday'
    _rec_name = 'holiday_date'

    is_full_day = fields.Boolean('Is full day?', default=True)
    holiday_date = fields.Date('Holiday Date')
    start_time = fields.Float('Start Time')
    end_time = fields.Float('End Time')



class project_booking_anchor(models.Model):

    _name = 'project.booking.anchor'

    name = fields.Char(string="Anchor Number")
    anchor_type_id = fields.Many2one('anchor.type', string="Anchor Type")
    anchor_size_id = fields.Many2one('anchor.size', string="Anchor Size")
    anchor_qty = fields.Char(string="Anchor Quantity")
    project_booking_id = fields.Many2one('project.booking', string="Project Booking")
    feed_project_booking_id = fields.Many2one('project.booking', string="Project Booking")
    failer_qty = fields.Char(string="Quantity Of Failures")
    an_complexity = fields.Selection([('simple', 'Simple'), ('medium', 'Medium'), ('complex', 'Complex')], string='Anchor complexity')
    equipment_id = fields.Many2one('equipment.equipment', string="Equipment")

    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()

    @api.model
    def create(self, vals):
        if vals.get('anchor_type_id') and vals.get('anchor_size_id'):
            if isinstance(vals.get('anchor_type_id'), int) == False:
                equipment = self.env['anchor.size.type'].search(
                    [
                        ('anchor_type_id', '=', int(eval(vals.get('anchor_type_id')))),
                        ('equipment_id', '!=', False),
                        ('anchor_size_ids', '=', int(eval(vals.get('anchor_size_id'))))
                    ],
                limit=1)
            else:
                equipment = self.env['anchor.size.type'].search(
                    [
                        ('anchor_type_id', '=', int(vals.get('anchor_type_id'))),
                        ('equipment_id', '!=', False),
                        ('anchor_size_ids', '=', int(vals.get('anchor_size_id')))
                    ],
                limit=1)
            if equipment:
                vals['equipment_id'] = equipment.equipment_id.id
        return super(project_booking_anchor, self).create(vals)

class project_booking(models.Model):
    _inherit = 'project.booking'


    time_booking_ids = fields.One2many('timeslot.booking', 'pr_booking_id', string="Booking Time")
    start_date_time = fields.Datetime('Start Date & Time')
    end_date_time = fields.Datetime('End Date & Time')
    booking_type = fields.Selection([('normal', 'Normal'), ('special', 'Dedicated Support'), ('sic', 'SIC Booking')], string='Booking Type')
    project_booking_anchor_ids = fields.One2many('project.booking.anchor', 'project_booking_id', string="Anchor Details")
    delay_time = fields.Float('Delay Duration', track_visibility='onchange')
    delay_remark = fields.Text('Delay Remarks', track_visibility='onchange')
    feedback_anchor_ids = fields.One2many('project.booking.anchor', 'feed_project_booking_id', string="FeedBack Anchor")
    testing_start_time = fields.Datetime('Actual Start Date & Time')
    testing_end_time = fields.Datetime('Actual End Date & Time')
    testing_duretion = fields.Char('Total Duration')
    testing_remark = fields.Char('Remarks')
    reminder_count = fields.Integer('Reminder Count')
    reminder_time = fields.Datetime('Last Reminder')
    reminder_history = fields.One2many('pt.reminder', 'pr_book_id', string="Reminder History")
    show_cancel_button = fields.Boolean('Show Cancel Button')
    is_cancel_from_tester = fields.Boolean('Cancel From Tester')
    final_start_dtime = fields.Datetime('Final Start Time')
    final_end_dtime = fields.Datetime('Final End Time')
    add_accept_button = fields.Boolean('Show Accept Button', default=False)
    internal_state_app = fields.Selection([('start', 'Start'), ('Feedback', 'Feedback'), ('done', 'Done')], string='Status', default='start', copy=False)
    is_swap_req_sent = fields.Boolean("Is Swap Req. Sent?", help="Technical field to hide some button related to tester swap by tester.")
    is_swap_req_get = fields.Boolean("Is Swap Req. Get?", help="Technical field to hide some button related to tester swap by tester. Ticked when another tester get req.")
    is_swap_req_accepted = fields.Boolean("Is Swap Req. Accepted To?", help="Technical field to hide some button related to tester swap by tester from.")
    is_swap_req_rejected = fields.Boolean("Is Swap Req. Rejected To?", help="Technical field to hide some button related to tester swap by tester.")
    from_swap_booking_id = fields.Many2one('project.booking', "Swap Requested From", help="it will store booking id from tester requested.")
    to_swap_req_booking_id = fields.Many2one('project.booking', "Swap Requested To", help="it will store reqested booking id.")
    sic_required_hours = fields.Float('Required Hours')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(project_booking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if not self.env.user.has_group('hilti_modifier_accessrights.group_hilti_cs_engineer') and not self.env.user.has_group('hilti_modifier_accessrights.group_hilti_account_manager'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button[@string='Swap Booking']"):
                modifiers = json.loads(node.get("modifiers", '{}'))
                modifiers['invisible'].insert(0, '|')
                modifiers['invisible'].append(('final_start_dtime', '<=', datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
                node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def get_mytask_state_app(self, mytask_id):
        mytask_obj = self.search([('id', '=', mytask_id)], limit=1)
        if mytask_id:
            if mytask_obj.status == 'pending':
                return "Pending"
            elif mytask_obj.status == 'started':
                if mytask_obj.testing_end_time:
                    return "Stop"
                else:
                    return "Start"
            elif mytask_obj.status == 'completed':
                return "Completed"
            else:
                return False

    @api.multi
    def get_anchor_details_app(self, mytask_id):
        mytask_obj = self.search([('id', '=', mytask_id)], limit=1)
        anchor_list = []
        for anchor in mytask_obj.project_booking_anchor_ids:
            vals = {}
            vals['anchor_number'] = anchor.name
            vals['anchor_type'] = anchor.anchor_type_id.name if anchor.anchor_type_id.name else ''
            vals['anchor_size'] = anchor.anchor_size_id.name if anchor.anchor_size_id.name else ''
            vals['anchor_qty'] = anchor.anchor_qty or ''
            vals['an_complexity'] = anchor.an_complexity
            vals['equipment'] = anchor.equipment_id.name if anchor.equipment_id.name else ''
            vals['id'] = anchor.id
            anchor_list.append(vals)
        return anchor_list

    @api.multi
    def update_mytask_feedback_app(self, mytask_id, vals, remarks):
        mytask_obj = self.search([('id', '=', mytask_id)], limit=1)
        if mytask_id:
            anchor_list = []
            for anchor in vals:
                anchor_type_obj = self.env['anchor.type'].search([('name', '=', anchor.get('anchor_type_id', ''))],limit=1)
                anchor_size_obj = self.env['anchor.size'].search([('name', '=', anchor.get('anchor_size_id', ''))],limit=1)

                anchor_dict = {}
                anchor_dict['anchor_type_id'] = anchor_type_obj.id if anchor_type_obj else ''
                anchor_dict['anchor_size_id'] = anchor_size_obj.id if anchor_size_obj else ''
                anchor_dict['anchor_qty'] = anchor.get('anchor_qty', '')
                anchor_dict['name'] = anchor.get('anchor_number', '')
                anchor_dict['an_complexity'] = anchor.get('an_complexity', '')
                anchor_dict['failer_qty'] = anchor.get('failer_qty', '')
                anchor_dict['feed_project_booking_id'] = mytask_id
                anchor_list.append((0, 0, anchor_dict))

            if mytask_obj and anchor_list:
                mytask_obj.feedback_anchor_ids = anchor_list
                mytask_obj.status = 'completed'
                mytask_obj.testing_remark = remarks or ''
                return True
        else:
            return False

    @api.multi
    def copy(self):
        raise Warning(_("If you want duplicate record then use re-book function."))
        return super(project_booking, self).copy()

    @api.model
    def create(self, vals):
        ctx = {}
        ctx = self._context.copy()
        if self._context and 'create_from_website' not in self._context:
            if vals['booking_type'] in ['normal'] and not vals.get('time_booking_ids'):
                raise Warning(_("Please select timeslot."))
            if vals['booking_type'] in ['normal', 'special'] and not vals.get('project_booking_anchor_ids'):
                raise Warning(_("Please select Anchor."))
            if vals and vals.get('project_booking_anchor_ids'):
                ctx.update({'parent_create_anchor_ids': vals['project_booking_anchor_ids']})
            if vals and 'booking_type' in vals.keys():
                local = pytz.timezone(self.env.user.tz)
                total_hours = []
                all_anchors = []
                for an in vals['project_booking_anchor_ids']:
                    type_an = self.env['anchor.master'].search([('anchor_type_id','=', an[2]['anchor_type_id'])])
                    if an[2]['an_complexity'] == 'complex':
                        total_hours.append(str(float(type_an.complex_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                    if an[2]['an_complexity'] == 'simple':
                        total_hours.append(str(float(type_an.simple_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                    if an[2]['an_complexity'] == 'medium':
                        total_hours.append(str(float(type_an.medium_time) * float(an[2]['anchor_qty'])).decode('utf-8'))
                    all_anchors.append([str(an[2]['anchor_size_id']).decode('utf-8'),str(an[2]['anchor_type_id']).decode('utf-8')])
                if vals['sid_required'] == False:
                    sic = 'no'
                else:
                    sic = 'yes'
                postal_code = self.env['postal.code'].search([('id', '=', vals['postal_code'])])
                if postal_code:
                    postal_code = postal_code.name
                if vals['booking_type'] in ['special']:
                    check_dt_start = datetime.strptime(vals['start_date_time'], "%Y-%m-%d %H:%M:%S")
                    start_date = pytz.utc.localize(check_dt_start, is_dst=None).astimezone(local).date()
                    start_time_formate = pytz.utc.localize(check_dt_start, is_dst=None).astimezone(local).time()
                    start_time = start_time_formate.hour+start_time_formate.minute/60.0
                    check_dt_end = datetime.strptime(vals['end_date_time'], "%Y-%m-%d %H:%M:%S")
                    end_date = pytz.utc.localize(check_dt_end, is_dst=None).astimezone(local).date()
                    end_time_formate = pytz.utc.localize(check_dt_end, is_dst=None).astimezone(local).time()
                    end_time = end_time_formate.hour+end_time_formate.minute/60.0
                    if vals['booking_type'] in ['special']:
                        booking_logic = self.sudo().dedicated_booking_logic(start_date, start_time, end_date, end_time,total_hours, all_anchors, vals['project_id'], sic, postal_code)
                        if booking_logic:
                            tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
                            vals.update({'user_tester_id': tester_id.id})
                        else:
                            vals.update({'add_accept_button': True})
                            # raise Warning(_("Testers are not available for the booking on (selected date time).Please select another date and time for your booking. Sorry for the inconvenience. Thank You."))
#                     if vals['booking_type'] in ['sic']:
#                         booking_logic = self.sudo().sic_booking_logic(start_date,start_time,end_time,postal_code)
#                         if booking_logic:
#                             tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
#                             vals.update({'user_tester_id': tester_id.id})
#                         else:
#                             raise Warning(_("No one tester is free please select another datetime."))
        result = super(project_booking, self.with_context(ctx)).create(vals)
        if result:
            if result.booking_type in ['special']:
                if result.start_date_time and result.end_date_time:
                    result.final_start_dtime = result.start_date_time
                    result.final_end_dtime = result.end_date_time
            if result.booking_type in ['normal', 'sic']:
                total_line = [line.id for line in result.time_booking_ids]
                time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
                if len(total_line) > 1 and time_slot.time_slot_based == False:
                    raise Warning(_("There can be only one booking timeslot for each booking. So, adding new timeslots, editing/deleting existing timeslots is not allowed. In case you want to change the timeslot for this booking, please use Re-schedule button."))
                if total_line:
                    start = False
                    end = False
                    booking_date = False
                    for line in result.time_booking_ids:
                        if start == False:
                            start = "%d:%02d:%02d" % (int(line.start), (line.start * 60) % 60, (line.start * 3600) % 60)
                            booking_date = datetime.strptime(line.booking_date, "%Y-%m-%d").date()
                        end = "%d:%02d:%02d" % (int(line.end), (line.end * 60) % 60, (line.end * 3600) % 60)
                    sdt = datetime.combine(booking_date, datetime.strptime(start, "%H:%M:%S").time())
                    edt = datetime.combine(booking_date, datetime.strptime(end, "%H:%M:%S").time())
                    if sdt and edt:
                        local = pytz.timezone(self.env.user.tz)
                        start_date = local.localize(sdt, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        end_date = local.localize(edt, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        result.final_start_dtime = start_date
                        result.final_end_dtime = end_date

            if result.final_start_dtime and result.final_end_dtime:
                start_date_day_name = datetime.strftime(datetime.strptime(result.final_start_dtime, DEFAULT_SERVER_DATETIME_FORMAT), '%A')
                end_date_day_name = datetime.strftime(datetime.strptime(result.final_end_dtime, DEFAULT_SERVER_DATETIME_FORMAT), '%A')

                if (start_date_day_name in ["Sunday", "Saturday"] or end_date_day_name in ["Sunday", "Saturday"]) and result.booking_type not in ['special']:
                    raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))

                start_date = datetime.strftime(datetime.strptime(result.final_start_dtime, DEFAULT_SERVER_DATETIME_FORMAT), "%Y-%m-%d")
                end_date = datetime.strftime(datetime.strptime(result.final_end_dtime, DEFAULT_SERVER_DATETIME_FORMAT), "%Y-%m-%d")
                holidays = self.env['holiday.holiday'].search(['|', ('holiday_date', '=', start_date), ('holiday_date', '=', end_date)])
                if holidays and result.booking_type not in ['special']:
                    raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))
#         template = self.env.ref('hilti_modifier_customer_booking.mail_template_booking_details')
#         template.send_mail(result.id, force_send=True)
        return result

    @api.multi
    def write(self, vals):
        if vals and 'time_booking_ids' in vals.keys():
            raise Warning(_("You do not change Booking Timeslot."))
        res = super(project_booking, self).write(vals)
        for self_id in self:
            if vals and 'start_date_time' in vals.keys() or 'end_date_time' in vals.keys():
                self_id.final_start_dtime = self_id.start_date_time
                self_id.final_end_dtime = self_id.end_date_time
            if self_id.booking_type in ['normal', 'sic']:
                total_line = [line.id for line in self_id.time_booking_ids]
                time_slot = self_id.env['timeslot.master'].sudo().search([], limit=1)
                if len(total_line) > 1 and time_slot.time_slot_based == False:
                    raise Warning(_("There can be only one booking timeslot for each booking. So, adding new timeslots, editing/deleting existing timeslots is not allowed. In case you want to change the timeslot for this booking, please use Re-schedule button."))
            if vals and 'user_tester_id' in vals.keys() and self_id.booking_type in ['normal','sic']:
                start = False
                end = False
                booking_date = False
                for line in self_id.time_booking_ids:
                    if start == False:
                        start = "%d:%02d:%02d" % (int(line.start), (line.start * 60) % 60, (line.start * 3600) % 60)
                        booking_date = datetime.strptime(line.booking_date, "%Y-%m-%d").date()
                    end = "%d:%02d:%02d" % (int(line.end), (line.end * 60) % 60, (line.end * 3600) % 60)
                if booking_date and start and end:
                    sdt = datetime.combine(booking_date, datetime.strptime(start, "%H:%M:%S").time())
                    edt = datetime.combine(booking_date, datetime.strptime(end, "%H:%M:%S").time())
                    if sdt and edt:
                        local = pytz.timezone(self.env.user.tz)
                        start_date = local.localize(sdt, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        end_date = local.localize(edt, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        self_id.final_start_dtime = start_date
                        self_id.final_end_dtime = end_date
            if self_id.final_start_dtime and self_id.final_end_dtime:
                start_date_day_name = datetime.strftime(datetime.strptime(self_id.final_start_dtime, DEFAULT_SERVER_DATETIME_FORMAT), '%A')
                end_date_day_name = datetime.strftime(datetime.strptime(self_id.final_end_dtime, DEFAULT_SERVER_DATETIME_FORMAT), '%A')

                if (start_date_day_name in ["Sunday", "Saturday"] or end_date_day_name in ["Sunday", "Saturday"]) and self_id.booking_type not in ['special']:
                    raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))

                start_date = datetime.strftime(datetime.strptime(self_id.final_start_dtime, DEFAULT_SERVER_DATETIME_FORMAT), "%Y-%m-%d")
                end_date = datetime.strftime(datetime.strptime(self_id.final_end_dtime, DEFAULT_SERVER_DATETIME_FORMAT), "%Y-%m-%d")
                holidays = self.env['holiday.holiday'].search(['|', ('holiday_date', '=', start_date), ('holiday_date', '=', end_date)])
                if holidays and self_id.booking_type not in ['special']:
                    raise UserError(_('Please choose the booking type as "Dedicated Support" to make bookings on weekends and public hoidays.'))
            return res

    def sic_booking_logic(self, final_booking_date, start_time, end_time, postal_code):
        time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
        booking_before_time = self.env['ir.values'].get_default('admin.configuration', 'booking_before_time')
        booking_after_time = self.env['ir.values'].get_default('admin.configuration', 'booking_after_time')
        request_start_time = float(start_time)
        request_end_time = float(end_time)
        start_time_break = float(start_time) - booking_before_time
        end_time_break = float(end_time) + booking_after_time
        start_time = float(start_time) - booking_before_time
        end_time = float(end_time) + booking_after_time
        booking_date = datetime.strptime(str(final_booking_date), "%Y-%m-%d").date()
        start_time = "%02d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)
        end_time = "%02d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)
        dt_start = datetime.combine(booking_date, datetime.strptime(start_time, "%H:%M:%S").time())
        dt_end = datetime.combine(booking_date, datetime.strptime(end_time, "%H:%M:%S").time())
        local = pytz.timezone(self.env.user.tz)
        check_dt_start = datetime.strptime(str(dt_start), "%Y-%m-%d %H:%M:%S")
        check_dt_end = datetime.strptime(str(dt_end), "%Y-%m-%d %H:%M:%S")
        dt_start = local.localize(dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        dt_end = local.localize(dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        dt_start = datetime.strptime(dt_start, "%Y-%m-%d %H:%M:%S")
        dt_end = datetime.strptime(dt_end, "%Y-%m-%d %H:%M:%S")
        start_date_day_name = datetime.strftime(booking_date, '%A')
        end_date_day_name = datetime.strftime(booking_date, '%A')
        reserved_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['special', 'sic', 'normal'])])
        used_booking_order = []
        for booking in reserved_booking_ids:
            if booking.final_start_dtime and booking.final_end_dtime:
                start_datetime = datetime.strptime(booking.final_start_dtime, "%Y-%m-%d %H:%M:%S")
                end_datetime = datetime.strptime(booking.final_end_dtime, "%Y-%m-%d %H:%M:%S")
                if not end_datetime < dt_start and not start_datetime > dt_end:
                    used_booking_order.append(booking.id)

        # Find overtime or holidays--------------------------------------------
        ot_start_time = self.env['ir.values'].get_default('admin.configuration', 'ot_start_time')
        ot_end_time = self.env['ir.values'].get_default('admin.configuration', 'ot_end_time')

        dt_start_ot_1 = datetime.combine(datetime.strptime(str(booking_date), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(ot_start_time), (ot_start_time*60) % 60, (ot_start_time*3600) % 60),"%H:%M:%S").time())
        dt_end_ot_1 = datetime.combine(datetime.strptime(str(booking_date), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(23.98), (23.98*60) % 60, (23.98*3600) % 60),"%H:%M:%S").time())
        dt_start_ot_2 = datetime.combine(datetime.strptime(str(booking_date), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (0,00,00 ),"%H:%M:%S").time())
        dt_end_ot_2 = datetime.combine(datetime.strptime(str(booking_date), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(ot_end_time), (ot_end_time*60) % 60, (ot_end_time*3600) % 60),"%H:%M:%S").time())
        is_holyday = False
        overtime = False
        if start_date_day_name in ["Sunday", "Saturday"]:
            is_holyday =True
        if not is_holyday:
            holidays = self.env['holiday.holiday'].search([('holiday_date', '=', booking_date)])
            if holidays:
                if holidays.is_full_day == False:
                    if start_time >= holidays.start_time and start_time <= holidays.end_time:
                        is_holyday = True
                    if end_time >= holidays.start_time and end_time <= holidays.end_time:
                        is_holyday = True
                else:
                    is_holyday = True

        if not is_holyday:
            serach_ot_start = False
            serach_ot_end = False
            if (request_start_time < time_slot.lunch_start_time < request_end_time) or (request_start_time < time_slot.lunch_end_time < request_end_time):
                 return False
            if (check_dt_start >= dt_start_ot_1) and (dt_end_ot_1 >= check_dt_end):
                serach_ot_start= check_dt_start
                serach_ot_end= check_dt_end
                overtime = True
            if (check_dt_start >= dt_start_ot_2) and (dt_end_ot_2 >= check_dt_end):
                serach_ot_start= check_dt_start
                serach_ot_end= check_dt_end
                overtime = True
            if (check_dt_start <= dt_start_ot_1 <= check_dt_end):
                serach_ot_start= dt_start_ot_1
                serach_ot_end= check_dt_end
                overtime = True
            if (check_dt_start <= dt_end_ot_1 <= check_dt_end):
                serach_ot_start= check_dt_start
                serach_ot_end= dt_end_ot_1
                overtime = True
            if (check_dt_start <= dt_start_ot_2 <= check_dt_end):
                serach_ot_start= dt_start_ot_2
                serach_ot_end= check_dt_end
                overtime = True
            if (check_dt_start <= dt_end_ot_2 <= check_dt_end):
                serach_ot_start= check_dt_start
                serach_ot_end= dt_end_ot_2
                overtime = True
            if serach_ot_start and serach_ot_end:
                serach_ot_start = local.localize(serach_ot_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                serach_ot_end = local.localize(serach_ot_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                serach_ot_start = datetime.strptime(serach_ot_start, "%Y-%m-%d %H:%M:%S")
                serach_ot_end = datetime.strptime(serach_ot_end, "%Y-%m-%d %H:%M:%S")
        all_tester = self.env['res.partner'].search([('type_of_user', '=', 'hilti_tester')])
        all_sic_tester = []
        if is_holyday:
            all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
            for ot in all_ot:
                if ot.t_re_id.status in ['approved']:
                    if ot.ot_start_date <= str(dt_start) and ot.ot_end_date >= str(dt_end):
                        all_sic_tester.append(ot.t_re_id.partner_id.id)
        if is_holyday == False and overtime == True:
            all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
            for ot in all_ot:
                 if ot.t_re_id.status in ['approved']:
                    if ot.ot_start_date <= str(serach_ot_start) and ot.ot_end_date >= str(serach_ot_end):
                        all_sic_tester.append(ot.t_re_id.partner_id.id)
        if is_holyday == False and overtime == False:
            all_sic_tester = [a.id for a in all_tester]
        if not all_sic_tester:
            return False
        sic_testers_free = []
        check_dt_start_un = local.localize(check_dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        check_dt_end_un = local.localize(check_dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if all_sic_tester:
            for ts in all_sic_tester:
                booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in used_booking_order if booking_order]
                all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                is_unavailable = False
                if all_unavailbel:
                    for aa in all_unavailbel:
                        if aa.is_half_leave and (aa.start_date <= str(check_dt_start_un) <= aa.end_date) or (aa.start_date <= str(check_dt_end_un) <= aa.end_date):
                            is_unavailable = True
                        if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                            is_unavailable = True
                if ts not in booking_tester_ids and is_unavailable == False:
                    sic_testers_free.append(ts)
            if not sic_testers_free:
                return False
            if sic_testers_free:
                zone_ids = self.env['zone.zone'].search([])
                testers_zone = []
                tester_availble_in_zone = []
                for zone in zone_ids:
                    for postal in zone.postal_code_ids:
                        if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                            if testers_zone:
                                break
                            else:
                                testers_zone.append(zone)
                if testers_zone:
                    slot_allocate = []
                    for tester in testers_zone[0].tester_ids:
                        if tester.id in sic_testers_free:
                            tester_availble_in_zone.append(tester.id)
                            break
                    if tester_availble_in_zone:
                        return tester_availble_in_zone[0]
                    else:
                        other_nearest_zone = []
                        postal_nearest_zone = []
                        for zoone in testers_zone[0].seq_ids:
                            for postal in zoone.postal_code_id:
                                if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                    postal_nearest_zone = [aa for aa in zoone.zone_ids]
                        not_postal_code = False
                        if postal_nearest_zone:
                           for ne_tester in postal_nearest_zone:
                                for tester in ne_tester.tester_ids:
                                    if tester.id in sic_testers_free:
                                        tester_availble_in_zone.append(tester.id)
                                        break
                                if tester_availble_in_zone:
                                      not_postal_code = True
                    if tester_availble_in_zone:
                        return tester_availble_in_zone[0]
                    else:
                        return False


    def dedicated_booking_logic(self,start_date,start_time,end_date,end_time,total_hours, all_anchors, project_id, sic, postal_code):
        booking_ids = []
        special_booking = []
        slot_time = sum([float(eval(a)) for a in total_hours])
        time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
        booking_before_time = self.env['ir.values'].get_default('admin.configuration', 'booking_before_time')
        booking_after_time = self.env['ir.values'].get_default('admin.configuration', 'booking_after_time')
        request_start_time = float(start_time)
        request_end_time = float(end_time)
        start_time = float(start_time) - booking_before_time
        end_time = float(end_time) + booking_after_time
        search_timeslot = []
        reuired_equipment = []
        special_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['special']),('status', 'not in', ['cancelled', 'completed'])])
        if start_time < 00.00:
            l_start_time = "%02d:%02d:%02d" % (int(start_time + 24), ((start_time + 24)*60) % 60, ((start_time + 24)*3600) % 60)
        else:
            l_start_time = "%02d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)
        if end_time >= 24.00:
            l_end_time = "%02d:%02d:%02d" % (int(end_time-24), ((end_time-24)*60) % 60, ((end_time-24)*3600) % 60)
        else:
            l_end_time = "%02d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)
        booking_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
        booking_date_1 = datetime.strptime(str(end_date), "%Y-%m-%d").date()
        if start_time < 00.00:
            booking_date = booking_date + timedelta(days=1)
            dt_start = datetime.combine(booking_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
        else:
            dt_start = datetime.combine(booking_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
        if end_time >= 24.00:
            booking_date_1 = booking_date_1 + timedelta(days=1)
            dt_end = datetime.combine(booking_date_1, datetime.strptime(l_end_time, "%H:%M:%S").time())
        else:
            dt_end = datetime.combine(booking_date_1, datetime.strptime(l_end_time, "%H:%M:%S").time())
        local = pytz.timezone(self.env.user.tz)
        check_dt_start = datetime.strptime(str(dt_start), "%Y-%m-%d %H:%M:%S")
        check_dt_end = datetime.strptime(str(dt_end), "%Y-%m-%d %H:%M:%S")
        dt_start = local.localize(dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        dt_end = local.localize(dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        dt_start = datetime.strptime(dt_start, "%Y-%m-%d %H:%M:%S")
        dt_end = datetime.strptime(dt_end, "%Y-%m-%d %H:%M:%S")
        start_date_day_name = datetime.strftime(booking_date, '%A')
        end_date_day_name = datetime.strftime(booking_date_1, '%A')
        for special in special_booking_ids:
            if special.start_date_time and special.end_date_time:
                special_start_datetime = datetime.strptime(special.start_date_time, "%Y-%m-%d %H:%M:%S")
                special_end_datetime = datetime.strptime(special.end_date_time, "%Y-%m-%d %H:%M:%S")
                if not special_end_datetime < dt_start and not special_start_datetime > dt_end:
                    special_booking.append(special.id)
        normal_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['normal', 'sic']),('status', 'not in', ['cancelled', 'completed'])])
        if normal_booking_ids:
            for book in normal_booking_ids:
                if book.final_end_dtime and book.final_start_dtime:
                    final_start_dtime = datetime.strptime(book.final_start_dtime, "%Y-%m-%d %H:%M:%S")
                    final_end_dtime = datetime.strptime(book.final_end_dtime, "%Y-%m-%d %H:%M:%S")
                    if not final_start_dtime < dt_start and not final_end_dtime > dt_end:
                        booking_ids.append(book.id)
        all_booked_ids = booking_ids + special_booking
        if all_anchors and all_anchors[0] and all_anchors[0] != 'sic_booking':
            for an in all_anchors:
                equipment = self.env['anchor.size.type'].search(
                        [
                            ('anchor_type_id', '=', int(eval(an[1]))),
                            ('equipment_id', '!=', False),
                            ('anchor_size_ids', '=', int(eval(an[0])))
                        ],
                    limit=1)
    
                if equipment:
                    reuired_equipment.append(equipment.equipment_id.id)
            reuired_equipment = list(set(reuired_equipment))
        for eq in reuired_equipment:
            equipment = self.env['equipment.equipment'].browse([eq])
            master_total_eq = equipment.qty
            total_remaining = 0
            used_eq = 0
            for booking in all_booked_ids:
                pr_book = self.env['project.booking'].browse([booking])
                all_pr_eq = [an.equipment_id.id for an in pr_book.project_booking_anchor_ids if an.equipment_id and an.equipment_id.id]
                for an in list(set(all_pr_eq)):
                    if an == eq:
                        used_eq += 1
            if all_booked_ids:
                total_remaining = int(master_total_eq) - int(used_eq)
                if total_remaining <= 0:
                    return False
        project_id_browse = self.env['project.project'].browse([int(project_id)])
        reserved_tester_free = []
        ot_start_time = self.env['ir.values'].get_default('admin.configuration', 'ot_start_time')
        ot_end_time = self.env['ir.values'].get_default('admin.configuration', 'ot_end_time')
        dt_end_ot = datetime.combine(datetime.strptime(str(booking_date + timedelta(days=1)), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(ot_end_time), (ot_end_time*60) % 60, (ot_end_time*3600) % 60),"%H:%M:%S").time())
        dt_start_ot = datetime.combine(datetime.strptime(str(booking_date), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(ot_start_time), (ot_start_time*60) % 60, (ot_start_time*3600) % 60),"%H:%M:%S").time())
        is_holyday = False
        overtime = False
        if start_date_day_name in ["Sunday", "Saturday"] or end_date_day_name in ["Sunday", "Saturday"]:
            is_holyday =True
        if not is_holyday:
            holidays = self.env['holiday.holiday'].search(['|', ('holiday_date', '=', booking_date), ('holiday_date', '=', booking_date_1)])
            if holidays:
                for a in holidays:
                    if a.is_full_day == False:
                        if start_time >= a.start_time and start_time <= a.end_time:
                            is_holyday = True
                        if end_time >= a.start_time and end_time <= a.end_time:
                            is_holyday = True
                    else:
                        is_holyday = True
        if not is_holyday:
            serach_ot_start = False
            serach_ot_end = False
            not_ot = False
            if booking_date == booking_date_1:
                dt_end_ot_sameday = datetime.combine(datetime.strptime(str(booking_date), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(ot_end_time), (ot_end_time*60) % 60, (ot_end_time*3600) % 60),"%H:%M:%S").time())
                if (dt_end_ot_sameday <= check_dt_start <= dt_start_ot) and (dt_end_ot_sameday <= check_dt_end <= dt_start_ot):
                    not_ot = True
                    if (request_start_time < time_slot.lunch_start_time < request_end_time) or (request_start_time < time_slot.lunch_end_time < request_end_time):
                         return False
            if (check_dt_start <= dt_start_ot <= check_dt_end) and not_ot == False:
                serach_ot_start= dt_start_ot
                serach_ot_end= check_dt_end
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < ot_start_time) or (start_time < time_slot.lunch_end_time < ot_start_time):
                    return False
            if (check_dt_start >= dt_start_ot) and (dt_end_ot >= check_dt_end) and not_ot == False:
                serach_ot_start= check_dt_start
                serach_ot_end= check_dt_end
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < end_time) or (start_time < time_slot.lunch_end_time < end_time):
                    return False
            if (check_dt_start >= dt_start_ot) and (dt_end_ot <= check_dt_end) and not_ot == False:
                serach_ot_start= check_dt_end
                serach_ot_end= dt_end_ot
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < end_time) or (start_time < time_slot.lunch_end_time < end_date):
                    return False
            if (check_dt_start <= dt_start_ot) and (dt_end_ot >= check_dt_end) and not_ot == False:
                serach_ot_start= dt_start_ot
                serach_ot_end= check_dt_end
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < ot_start_time) or (start_time < time_slot.lunch_end_time < ot_start_time):
                    return False

            if (check_dt_start <= dt_start_ot) and (dt_end_ot <= check_dt_end) and not_ot == False:
                serach_ot_start= dt_start_ot
                serach_ot_end= dt_end_ot
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < ot_start_time) or (start_time < time_slot.lunch_end_time < ot_start_time):
                    return False

            if (check_dt_start <= dt_end_ot <= check_dt_end) and not_ot == False:
                serach_ot_start= check_dt_start
                serach_ot_end= dt_end_ot
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < end_time) or (start_time < time_slot.lunch_end_time < end_time):
                    return False
            dt_end_ot = datetime.combine(datetime.strptime(str(booking_date_1), DEFAULT_SERVER_DATE_FORMAT), datetime.strptime("%d:%02d:%02d" % (int(ot_end_time), (ot_end_time*60) % 60, (ot_end_time*3600) % 60),"%H:%M:%S").time())
            if (check_dt_start <= dt_end_ot <= check_dt_end) and not_ot == False:
                serach_ot_start= check_dt_start
                serach_ot_end= dt_end_ot
                overtime = True
                not_ot = True
                if (start_time < time_slot.lunch_start_time < end_time) or (start_time < time_slot.lunch_end_time < end_time):
                    return False
            if serach_ot_start and serach_ot_end:
                serach_ot_start = local.localize(serach_ot_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                serach_ot_end = local.localize(serach_ot_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                serach_ot_start = datetime.strptime(serach_ot_start, "%Y-%m-%d %H:%M:%S")
                serach_ot_end = datetime.strptime(serach_ot_end, "%Y-%m-%d %H:%M:%S")
        if project_id_browse.tester_ids:
            reserved_tester_list = []
            if is_holyday:
                all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
                for ot in all_ot:
                    if ot.t_re_id.status in ['approved']:
                        if ot.ot_start_date <= str(dt_start) and ot.ot_end_date >= str(dt_end):
                            for a in project_id_browse.tester_ids:
                                if a.id == ot.t_re_id.partner_id.id:
                                    reserved_tester_list.append(ot.t_re_id.partner_id.id)
            if is_holyday == False and overtime == True:
                    all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
                    for ot in all_ot:
                         if ot.t_re_id.status in ['approved']:
                            if ot.ot_start_date <= str(serach_ot_start) and ot.ot_end_date >= str(serach_ot_end):
                                for a in project_id_browse.tester_ids:
                                    if a.id == ot.t_re_id.partner_id.id:
                                        reserved_tester_list.append(ot.t_re_id.partner_id.id)
            if is_holyday == False and overtime == False:
                reserved_tester_list = [a.id for a in project_id_browse.tester_ids]
            for ts in reserved_tester_list:
                booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in all_booked_ids if booking_order]
                all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                is_unavailable = False
                if all_unavailbel:
                    for aa in all_unavailbel:
                        if aa.is_half_leave and (aa.start_date <= str(dt_start) <= aa.end_date) or (aa.start_date <= str(dt_end) <= aa.end_date):
                            is_unavailable = True
                        if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                            is_unavailable = True
                if ts not in booking_tester_ids and is_unavailable == False:
                    reserved_tester_free.append(ts)
                    break
        if reserved_tester_free:
            return reserved_tester_free[0]
        else:
            sic_testers_free = []
            no_one_booking = []
            slot_asssign = []
            all_tester = self.env['res.partner'].search([('type_of_user', '=', 'hilti_tester')])
            all_sic_tester = []
            if str(sic) == 'yes':
                if is_holyday:
                    all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
                    for ot in all_ot:
                        if ot.t_re_id.status in ['approved']:
                            if ot.ot_start_date <= str(dt_start) and ot.ot_end_date >= str(dt_end):
                                for pr in ot.t_re_id.partner_id.project_ids:
                                    if pr.id == int(project_id):
                                        all_sic_tester.append(ot.t_re_id.partner_id.id)
                if is_holyday == False and overtime == True:
                    all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
                    for ot in all_ot:
                         if ot.t_re_id.status in ['approved']:
                            if ot.ot_start_date <= str(serach_ot_start) and ot.ot_end_date >= str(serach_ot_end):
                                for pr in ot.t_re_id.partner_id.project_ids:
                                    if pr.id == int(project_id):
                                        all_sic_tester.append(ot.t_re_id.partner_id.id)

                if is_holyday == False and overtime == False:
                    for tes in all_tester:
                        for pr in tes.project_ids:
                            if pr.id == int(project_id):
                                all_sic_tester.append(tes.id)
                if not all_sic_tester:
                    return False
            else:
                if is_holyday:
                    all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
                    for ot in all_ot:
                        if ot.t_re_id.status in ['approved']:
                            if ot.ot_start_date <= str(dt_start) and ot.ot_end_date >= str(dt_end):
                                all_sic_tester.append(ot.t_re_id.partner_id.id)
                if is_holyday == False and overtime == True:
                    all_ot = self.env['ot.request'].search([('t_re_id', '!=', False)])
                    for ot in all_ot:
                         if ot.t_re_id.status in ['approved']:
                            if ot.ot_start_date <= str(serach_ot_start) and ot.ot_end_date >= str(serach_ot_end):
                                all_sic_tester.append(ot.t_re_id.partner_id.id)
                if is_holyday == False and overtime == False:
                    all_sic_tester = [a.id for a in all_tester]
            if all_sic_tester:
                for ts in all_sic_tester:
                    booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in all_booked_ids if booking_order]
                    all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                    is_unavailable = False
                    if all_unavailbel:
                        for aa in all_unavailbel:
                            if aa.is_half_leave and (aa.start_date <= str(dt_start) <= aa.end_date) or (aa.start_date <= str(dt_end) <= aa.end_date):
                                is_unavailable = True
                            if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                is_unavailable = True
                    if ts not in booking_tester_ids and is_unavailable == False:
                        sic_testers_free.append(ts)
            if not sic_testers_free:
                return False
            if sic_testers_free:
                zone_ids = self.env['zone.zone'].search([])
                testers_zone = []
                tester_availble_in_zone = []
                for zone in zone_ids:
                    for postal in zone.postal_code_ids:
                        if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                            if testers_zone:
                                break
                            else:
                                testers_zone.append(zone)
                if testers_zone:
                    slot_allocate = []
                    no_one_booking_tester = []
                    for tester in testers_zone[0].tester_ids:
                        if tester.id in sic_testers_free:
                            tester_availble_in_zone.append(tester.id)
                            break
                    if tester_availble_in_zone:
                        return tester_availble_in_zone[0]
                    else:
                        other_nearest_zone = []
                        postal_nearest_zone = []
                        for zoone in testers_zone[0].seq_ids:
                            for postal in zoone.postal_code_id:
                                if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                    postal_nearest_zone = [aa for aa in zoone.zone_ids]
                        not_postal_code = False
                        if postal_nearest_zone:
                           for ne_tester in postal_nearest_zone:
                                for tester in ne_tester.tester_ids:
                                    if tester.id in sic_testers_free:
                                        tester_availble_in_zone.append(tester.id)
                                        break
                                if tester_availble_in_zone:
                                      not_postal_code = True
                    if tester_availble_in_zone:
                        return tester_availble_in_zone[0]
                    else:
                        return False

    def booking_logic_dynamic(self, booking_date,total_hours, all_anchors, project_id, sic, postal_code, slot_time):
        booking_before_time = self.env['ir.values'].get_default('admin.configuration', 'booking_before_time')
        booking_after_time = self.env['ir.values'].get_default('admin.configuration', 'booking_after_time')
        booking_date_holyday = datetime.strptime(str(booking_date), "%Y-%m-%d").date()
        half_holidays = self.env['holiday.holiday'].search([('holiday_date', '=', booking_date_holyday), ('is_full_day', '=', False)])
        time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
        normal_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['normal', 'sic', 'special']), ('status', 'not in', ['cancelled', 'completed'])])
        all_end_time = [time.timeslot_end_id.end_time for time in time_slot.time_slot_ids]
        if slot_time == False:
            slot_time = sum([float(eval(a)) for a in total_hours])
            match_timeslot = []
            match_timeslot_all_ids = []
            if half_holidays:
                half_day_time = []
                all_start_time = [time.timeslot_start_id.start_time for time in time_slot.time_slot_ids]
                all_end_time = [time.timeslot_end_id.end_time for time in time_slot.time_slot_ids]
                for start in all_start_time:
                    if start and (float(start) + float(slot_time) in all_end_time):
                        match_timeslot.append([start, (float(start) + float(slot_time))])
                        match_timeslot_all_ids.append([start, (float(start) + float(slot_time))])
                for all in match_timeslot:
                    if all[0] >= half_holidays.start_time and all[0] <= half_holidays.end_time:
                        half_day_time.append(all)
                    if all[1] >= half_holidays.start_time and all[1] <= half_holidays.end_time:
                        half_day_time.append(all)
                if half_day_time:
                    match_timeslot = [aa for aa in match_timeslot if aa not in half_day_time]
                    match_timeslot_all_ids = [aa for aa in match_timeslot]
            else:
                all_start_time = [time.timeslot_start_id.start_time for time in time_slot.time_slot_ids]
                all_end_time = [time.timeslot_end_id.end_time for time in time_slot.time_slot_ids]
                for start in all_start_time:
                    if start and (float(start) + float(slot_time) in all_end_time):
                        match_timeslot.append([start, (float(start) + float(slot_time))])
                        match_timeslot_all_ids.append([start, (float(start) + float(slot_time))])
        else:
            nearest_time_slot = float(slot_time) + 0.30
            if nearest_time_slot >= max(all_end_time):
                slot_time = False
                match_timeslot_all_ids = []
            else:
                slot_time = float(nearest_time_slot)
                # match slot for find all slot which you want customer
                match_timeslot = []
                match_timeslot_all_ids = []
                if half_holidays:
                    half_day_time = []
                    all_start_time = [time.timeslot_start_id.start_time for time in time_slot.time_slot_ids]
                    all_end_time = [time.timeslot_end_id.end_time for time in time_slot.time_slot_ids]
                    for start in all_start_time:
                        if start and (float(start) + float(slot_time) in all_end_time):
                            match_timeslot.append([start, (float(start) + float(slot_time))])
                            match_timeslot_all_ids.append([start, (float(start) + float(slot_time))])
                    for all in match_timeslot:
                        if all[0] >= half_holidays.start_time and all[0] <= half_holidays.end_time:
                            half_day_time.append(all)
                        if all[1] >= half_holidays.start_time and all[1] <= half_holidays.end_time:
                            half_day_time.append(all)
                    if half_day_time:
                        match_timeslot = [aa for aa in match_timeslot if aa not in half_day_time]
                        match_timeslot_all_ids = [aa for aa in match_timeslot]
                else:
                    all_start_time = [time.timeslot_start_id.start_time for time in time_slot.time_slot_ids]
                    all_end_time = [time.timeslot_end_id.end_time for time in time_slot.time_slot_ids]
                    for start in all_start_time:
                        if start and (float(start) + float(slot_time) in all_end_time):
                            match_timeslot.append([start, (float(start) + float(slot_time))])
                            match_timeslot_all_ids.append([start, (float(start) + float(slot_time))])
        if not match_timeslot_all_ids:
            return [slot_time]
        else:
            match_timeslot_dict = {}
            match_timeslot_all_ids_dict = {}
            count = 0
            for nn in match_timeslot:
                count += 1
                match_timeslot_dict.update({count: nn})
                match_timeslot_all_ids_dict.update({count: nn})
            reuired_equipment = []
            slot_wise_booking = {}
            for match in match_timeslot_dict.keys():
                search_timeslot = []
                special_booking = []
                start_time = match_timeslot_dict[match][0] - booking_before_time
                end_time = match_timeslot_dict[match][1] + booking_after_time
                special_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['special']),('status', 'not in', ['cancelled', 'completed'])])
                l_start_time = "%02d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)
                l_end_time = "%02d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)
                booking_date = datetime.strptime(str(booking_date), "%Y-%m-%d").date()
                dt_start = datetime.combine(booking_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
                dt_end = datetime.combine(booking_date, datetime.strptime(l_end_time, "%H:%M:%S").time())
                local = pytz.timezone(self.env.user.tz)
                dt_start = local.localize(dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_end = local.localize(dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_start = datetime.strptime(dt_start, "%Y-%m-%d %H:%M:%S")
                dt_end = datetime.strptime(dt_end, "%Y-%m-%d %H:%M:%S")
                for special in special_booking_ids:
                    if special.start_date_time and special.end_date_time:
                        special_start_datetime = datetime.strptime(special.start_date_time, "%Y-%m-%d %H:%M:%S")
                        special_end_datetime = datetime.strptime(special.end_date_time, "%Y-%m-%d %H:%M:%S")
                        if not special_end_datetime < dt_start and not special_start_datetime > dt_end:
                            special_booking.append(special.id)
                normal_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['normal','sic']),('status', 'not in', ['cancelled', 'completed'])])
                booking_ids = []
                if normal_booking_ids:
                    for book in normal_booking_ids:
                        if book.final_end_dtime and book.final_start_dtime:
                            final_start_dtime = datetime.strptime(book.final_start_dtime, "%Y-%m-%d %H:%M:%S")
                            final_end_dtime = datetime.strptime(book.final_end_dtime, "%Y-%m-%d %H:%M:%S")
                            if not final_start_dtime < dt_start and not final_end_dtime > dt_end:
                                booking_ids.append(book.id)
                all_booked_ids = booking_ids + special_booking
                slot_wise_booking.update({match: all_booked_ids})
            #Check equipments are free for requested timeslot
            for an in all_anchors:
                equipment = self.env['anchor.size.type'].search(
                        [
                            ('anchor_type_id', '=', int(eval(an[1]))),
                            ('equipment_id', '!=', False),
                            ('anchor_size_ids', '=', int(eval(an[0])))
                        ],
                    limit=1)
                
                if equipment:
                    reuired_equipment.append(equipment.equipment_id.id)
            reuired_equipment = list(set(reuired_equipment))
            equipment_not_availbale = []
            for slow_wise in slot_wise_booking.keys():
                temp_continue = 0
                for eq in list(set(reuired_equipment)):
                    equipment = self.env['equipment.equipment'].browse([eq])
                    master_total_eq = equipment.qty
                    total_remaining = 0
                    used_eq = 0
                    for booking_order in slot_wise_booking[slow_wise]:
                        pr_book = self.env['project.booking'].browse([booking_order])
                        all_pr_eq = [an.equipment_id.id for an in pr_book.project_booking_anchor_ids if an.equipment_id and an.equipment_id.id]
                        for an in list(set(all_pr_eq)):
                            if an == eq:
                                used_eq += 1
                    total_remaining = int(master_total_eq) - int(used_eq)
                    if total_remaining <= 0:
                        if slow_wise in match_timeslot_all_ids_dict.keys():
                            del match_timeslot_all_ids_dict[slow_wise]
                            temp_continue = 1
                            equipment_not_availbale.append(slow_wise)
                if temp_continue == 1:
                   continue
            # No one time slot is free
            if not match_timeslot_all_ids_dict:
                return [slot_time]
            else:
                no_one_booking = []
                no_one_booking_tester = []
                slot_asssign = []
                for aaa in equipment_not_availbale:
                    del slot_wise_booking[aaa]
                project_id_browse = self.env['project.project'].browse([int(project_id)])
                reserved_tester_free = {}
                if project_id_browse.tester_ids:
                    reserved_tester_list = [a.id for a in project_id_browse.tester_ids]
                    for slow_wise in slot_wise_booking.keys():
                        if not slot_wise_booking[slow_wise]:

                            no_one_booking.append(match_timeslot_dict[slow_wise])
                        for ts in project_id_browse.tester_ids:
                            if not no_one_booking_tester:
                                no_one_booking_tester.append(ts.id)
                            booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                            if booking_tester_ids and slow_wise not in slot_asssign:
                                if ts.id not in booking_tester_ids:
                                    if ts.id in reserved_tester_free.keys():
                                        slot_asssign.append(slow_wise)
                                        if type(reserved_tester_free.get(ts.id)) != list:
                                            all_val = [reserved_tester_free.get(ts.id), match_timeslot_dict[slow_wise]]
                                            b_set = set(map(tuple,all_val))
                                            all_val = map(list,b_set)
                                            all_val.sort(key=lambda k: (k[0]), reverse=False)
                                            reserved_tester_free[ts.id] = all_val
                                        else:
                                            all_val = reserved_tester_free.get(ts.id)
                                            for aa in all_val:
                                                if type(aa) != list:
                                                    all_val = [reserved_tester_free.get(ts.id)]
                                            all_val.append(match_timeslot_dict[slow_wise])
                                            b_set = set(map(tuple,all_val))
                                            all_val = map(list,b_set)
                                            all_val.sort(key=lambda k: (k[0]), reverse=False)
                                            reserved_tester_free[ts.id] = all_val
                                    else:
                                        reserved_tester_free.update({ts.id: match_timeslot_dict[slow_wise]})
                                        slot_asssign.append(slow_wise)
                    b_set = set(map(tuple,no_one_booking))
                    no_one_booking = map(list,b_set)
                    no_one_booking.sort(key=lambda k: (k[0]), reverse=False)
                    if no_one_booking_tester and no_one_booking:
                        reserved_tester_free[no_one_booking_tester[0]] = no_one_booking
                        no_one_booking_tester = []
                        no_one_booking = []
                # If no one reserved tester is available then
                for ts in reserved_tester_free.keys():
                    all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                    if all_unavailbel:
                        for aa in all_unavailbel:
                            if aa.is_half_leave:
                                remove_list = []
                                local = pytz.timezone(self.env.user.tz)
                                aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                    start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                    end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                    for time1 in reserved_tester_free[ts]:
                                        if (float(start_time) <= float(time1[0]) <= float(end_time)) or (float(start_time) <= float(time1[1]) <= float(end_time)):
                                            remove_list.append(time1)
                                for a in remove_list:
                                    reserved_tester_free[ts].remove(a)
                                if reserved_tester_free[ts] == []:
                                    del reserved_tester_free[ts]
                            if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                del reserved_tester_free[ts]
                if reserved_tester_free:
                    return reserved_tester_free
                if not reserved_tester_free:
                    sic_testers_free = {}
                    no_one_booking = []
                    slot_asssign = []
                    all_tester = self.env['res.partner'].search([('type_of_user', '=', 'hilti_tester')])
                    if str(sic) == 'yes':
                        all_sic_tester = []
                        for tes in all_tester:
                            for pr in tes.project_ids:
                                if pr.id == int(project_id):
                                    all_sic_tester.append(tes.id)
                        if not all_sic_tester:
                            return [slot_time]
                    else:
                        all_sic_tester = [a.id for a in all_tester]
                    for slow_wise in slot_wise_booking.keys():
                        booking_tester_ids_all = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                        for a in booking_tester_ids_all:
                            if a in all_sic_tester:
                                all_sic_tester.remove(a)
                    if all_sic_tester:
                        zone_ids = self.env['zone.zone'].search([])
                        testers_zone1 = []
                        for zone in zone_ids:
                            for postal in zone.postal_code_ids:
                                if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                    if testers_zone1:
                                        break
                                    else:
                                        testers_zone1.append(zone)
                        all_tester = [a.id for tester in testers_zone1 for a in tester.tester_ids]
                        for slow_wise in slot_wise_booking.keys():
                            for ts in all_tester:
                                if not slot_wise_booking[slow_wise]:
                                    no_one_booking.append(match_timeslot_dict[slow_wise])
                                booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                                if booking_tester_ids and slow_wise not in slot_asssign:
                                    if ts not in booking_tester_ids:
                                        if ts in sic_testers_free.keys():
                                            slot_asssign.append(slow_wise)
                                            if type(sic_testers_free.get(ts)) != list:
                                                all_val = [sic_testers_free.get(ts), match_timeslot_dict[slow_wise]]
                                                b_set = set(map(tuple,all_val))
                                                all_val = map(list,b_set)
                                                all_val.sort(key=lambda k: (k[0]), reverse=False)
                                                sic_testers_free[ts] = all_val
                                            else:
                                                all_val = sic_testers_free.get(ts)
                                                for aa in all_val:
                                                    if type(aa) != list:
                                                        all_val = [sic_testers_free.get(ts)]
                                                all_val.append(match_timeslot_dict[slow_wise])
                                                b_set = set(map(tuple,all_val))
                                                all_val = map(list,b_set)
                                                all_val.sort(key=lambda k: (k[0]), reverse=False)
                                                sic_testers_free[ts] = all_val
                                        else:
                                            sic_testers_free.update({ts: match_timeslot_dict[slow_wise]})
                                            slot_asssign.append(slow_wise)
                            for ts in all_sic_tester:
                                if not slot_wise_booking[slow_wise]:
                                    no_one_booking.append(match_timeslot_dict[slow_wise])
                                booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                                if booking_tester_ids and slow_wise not in slot_asssign:
                                    if ts not in booking_tester_ids:
                                        if ts in sic_testers_free.keys():
                                            slot_asssign.append(slow_wise)
                                            if type(sic_testers_free.get(ts)) != list:
                                                all_val = [sic_testers_free.get(ts), match_timeslot_dict[slow_wise]]
                                                b_set = set(map(tuple,all_val))
                                                all_val = map(list,b_set)
                                                all_val.sort(key=lambda k: (k[0]), reverse=False)
                                                sic_testers_free[ts] = all_val
                                            else:
                                                all_val = sic_testers_free.get(ts)
                                                for aa in all_val:
                                                    if type(aa) != list:
                                                        all_val = [sic_testers_free.get(ts)]
                                                all_val.append(match_timeslot_dict[slow_wise])
                                                b_set = set(map(tuple,all_val))
                                                all_val = map(list,b_set)
                                                all_val.sort(key=lambda k: (k[0]), reverse=False)
                                                sic_testers_free[ts] = all_val
                                        else:
                                            sic_testers_free.update({ts: match_timeslot_dict[slow_wise]})
                                            slot_asssign.append(slow_wise)
                    b_set = set(map(tuple,no_one_booking))
                    no_one_booking = map(list,b_set)
                    no_one_booking.sort(key=lambda k: (k[0]), reverse=False)
                    for ts in sic_testers_free.keys():
                        all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                        if all_unavailbel:
                            for aa in all_unavailbel:
                                if aa.is_half_leave:
                                    remove_list = []
                                    local = pytz.timezone(self.env.user.tz)
                                    aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                    aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                    start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                    end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                    start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                    end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                    if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                        start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                        end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                        for time1 in sic_testers_free[ts]:
                                            if (float(start_time) <= float(time1[0]) <= float(end_time)) or (float(start_time) <= float(time1[1]) <= float(end_time)):
                                                remove_list.append(time1)
                                    if remove_list:
                                        for a in remove_list:
                                            sic_testers_free[ts].remove(a)
                                            no_one_booking.append(a)
                                if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                    for a in sic_testers_free[ts]:
                                        no_one_booking.append(a)
                                    del sic_testers_free[ts]
                    b_set = set(map(tuple,no_one_booking))
                    no_one_booking = map(list,b_set)
                    no_one_booking.sort(key=lambda k: (k[0]), reverse=False)
                    if not sic_testers_free and not no_one_booking:
                        return [slot_time]
                    else:
                        zone_ids = self.env['zone.zone'].search([])
                        testers_zone = []
                        tester_availble_in_zone = {}
                        for zone in zone_ids:
                            for postal in zone.postal_code_ids:
                                if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                    if testers_zone:
                                        break
                                    else:
                                        testers_zone.append(zone)
                        if testers_zone:
                            slot_allocate = []
                            no_one_booking_tester = []
                            for tester in testers_zone[0].tester_ids:
                                if tester.id in sic_testers_free.keys():
                                    if not sic_testers_free[tester.id] in slot_allocate:
                                        slot_allocate.append(sic_testers_free[tester.id])
                                        tester_availble_in_zone[tester.id] = sic_testers_free[tester.id]
                                        del sic_testers_free[tester.id]
                                if no_one_booking:
                                    tester_is_not_available = False
                                    if 'passed_tester_id' in self._context and self._context.get('passed_tester_id') in all_sic_tester:
                                        all_sic_tester.remove(self._context.get('passed_tester_id'))
                                    if tester.id in all_sic_tester and not no_one_booking_tester:
                                        all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', tester.id)])
                                        if all_unavailbel:
                                            for aa in all_unavailbel:
                                                if aa.is_half_leave:
                                                    local = pytz.timezone(self.env.user.tz)
                                                    aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                                    aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                                    start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                                    end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                                    start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                                    end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                                    if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                                        start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                                        end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                                        for time1 in no_one_booking:
                                                            if (float(start_time) <= float(time1[0]) <= float(end_time)) or (float(start_time) <= float(time1[1]) <= float(end_time)):
                                                                tester_is_not_available = True
                                                if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                                    tester_is_not_available = True
                                        if tester_is_not_available == False:
                                            no_one_booking_tester.append(tester.id)
                            if no_one_booking and no_one_booking_tester:
                                if 'passed_timeslot_id' in self._context:
                                    if self._context.get('passed_timeslot_id') in tester_availble_in_zone.values():
                                        no_one_booking = []
                                if no_one_booking:
                                    if tester_availble_in_zone and no_one_booking_tester[0] in tester_availble_in_zone.keys():
                                        no_one_booking.append(tester_availble_in_zone[no_one_booking_tester[0]])
                                        tester_availble_in_zone[no_one_booking_tester[0]] = no_one_booking
                                    else:
                                        tester_availble_in_zone.update({no_one_booking_tester[0]: no_one_booking})
                                    no_one_booking = []
                                    no_one_booking_tester = []
                            if not sic_testers_free and not no_one_booking:
                                return tester_availble_in_zone
                                # I found all tester with timeslot ids and also search zone , in zone i found testers
                            else:

                                postal_nearest_zone = []
                                for zoone in testers_zone[0].seq_ids:
                                    for postal in zoone.postal_code_id:
                                        if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                            postal_nearest_zone = [aa for aa in zoone.zone_ids]
                                not_postal_code = False
                                if postal_nearest_zone:
                                    slot_allocate_1 = []
                                    no_one_booking_tester = []
                                    for ne_tester in postal_nearest_zone:
                                        for tester in ne_tester.tester_ids:
                                            if tester.id in sic_testers_free.keys():
                                                if not sic_testers_free[tester.id] in slot_allocate_1:
                                                    slot_allocate_1.append(sic_testers_free[tester.id])
                                                    tester_availble_in_zone[tester.id] = sic_testers_free[tester.id]
                                                    del sic_testers_free[tester.id]
                                                    not_postal_code = True
                                            if no_one_booking:
                                                if tester.id in all_sic_tester and not no_one_booking_tester:
                                                    no_one_booking_tester.append(tester.id)
                                    if no_one_booking and no_one_booking_tester:
                                        if 'passed_timeslot_id' in self._context:
                                            if self._context.get('passed_timeslot_id') in tester_availble_in_zone.values():
                                                no_one_booking = []
                                        if no_one_booking:
                                            tester_availble_in_zone[no_one_booking_tester[0]] = no_one_booking
                                            no_one_booking = []
                                            no_one_booking_tester = []
                                            not_postal_code = True
                            return tester_availble_in_zone

    def booking_logic(self, booking_date,total_hours, all_anchors, project_id, sic, postal_code, slot_time):
        booking_before_time = self.env['ir.values'].get_default('admin.configuration', 'booking_before_time')
        booking_after_time = self.env['ir.values'].get_default('admin.configuration', 'booking_after_time')
        booking_date_holyday = datetime.strptime(str(booking_date), "%Y-%m-%d").date()
        half_holidays = self.env['holiday.holiday'].search([('holiday_date', '=', booking_date_holyday), ('is_full_day', '=', False)])
        time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
        if slot_time == False:
            slot_time = sum([float(eval(a)) for a in total_hours])
            if half_holidays:
                half_day_time = []
                match_timeslot = [slot for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
                match_timeslot_all_ids = [slot.id for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
                for all in match_timeslot:
                    if all.timeslot_start_id.start_time >= half_holidays.start_time and all.timeslot_start_id.start_time <= half_holidays.end_time:
                        half_day_time.append(all.id)
                    if all.timeslot_end_id.end_time >= half_holidays.start_time and all.timeslot_end_id.end_time <= half_holidays.end_time:
                        half_day_time.append(all.id)
                if half_day_time:
                    match_timeslot = [aa for aa in match_timeslot if aa.id not in half_day_time]
                    match_timeslot_all_ids = [aa.id for aa in match_timeslot]
            else:
                match_timeslot = [slot for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
                match_timeslot_all_ids = [slot.id for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
        else:
            nearest_time_slot = [(slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) > float(slot_time)]
            if not nearest_time_slot:
                slot_time = False
                match_timeslot_all_ids = []
            else:
                slot_time = float(min(nearest_time_slot))
                # match slot for find all slot which you want customer
                if half_holidays:
                    half_day_time = []
                    match_timeslot = [slot for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
                    match_timeslot_all_ids = [slot.id for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
                    for all in match_timeslot:
                        if all.timeslot_start_id.start_time >= half_holidays.start_time and all.timeslot_start_id.start_time <= half_holidays.end_time:
                            half_day_time.append(all.id)
                        if all.timeslot_end_id.end_time >= half_holidays.start_time and all.timeslot_end_id.end_time <= half_holidays.end_time:
                            half_day_time.append(all.id)
                    if half_day_time:
                        match_timeslot = [aa for aa in match_timeslot if aa.id not in half_day_time]
                        match_timeslot_all_ids = [aa.id for aa in match_timeslot]
                else:
                    match_timeslot = [slot for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
                    match_timeslot_all_ids = [slot.id for slot in  time_slot.time_slot_ids if (slot.timeslot_end_id.end_time - slot.timeslot_start_id.start_time) == slot_time]
        if not match_timeslot_all_ids:
            return [slot_time]
        else:
            reuired_equipment = []
            slot_wise_booking = {}
            for match in match_timeslot:
                search_timeslot = []
                special_booking = []
                start_time = match.timeslot_start_id.start_time - booking_before_time
                end_time = match.timeslot_end_id.end_time + booking_after_time
                special_booking_ids = self.env['project.booking'].search([('booking_type', 'in', ['special']),('status', 'not in', ['cancelled', 'completed'])])
                l_start_time = "%02d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)
                l_end_time = "%02d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)
                booking_date = datetime.strptime(str(booking_date), "%Y-%m-%d").date()
                dt_start = datetime.combine(booking_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
                dt_end = datetime.combine(booking_date, datetime.strptime(l_end_time, "%H:%M:%S").time())
                local = pytz.timezone(self.env.user.tz)
                dt_start = local.localize(dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_end = local.localize(dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_start = datetime.strptime(dt_start, "%Y-%m-%d %H:%M:%S")
                dt_end = datetime.strptime(dt_end, "%Y-%m-%d %H:%M:%S")
                for special in special_booking_ids:
                    if special.start_date_time and special.end_date_time:
                        special_start_datetime = datetime.strptime(special.start_date_time, "%Y-%m-%d %H:%M:%S")
                        special_end_datetime = datetime.strptime(special.end_date_time, "%Y-%m-%d %H:%M:%S")
                        if not special_end_datetime < dt_start and not special_start_datetime > dt_end:
                            special_booking.append(special.id)
                search_timeslot.append(match.id)
                for slot in time_slot.time_slot_ids:
                    if not slot.timeslot_start_id.start_time > end_time and not slot.timeslot_end_id.end_time < start_time:
                        search_timeslot.append(slot.id)
                timeslot_booking_ids = self.env['timeslot.booking'].sudo().search([('booking_date', '=', booking_date),('time_slot_id', 'in', search_timeslot),('pr_booking_id', '!=', False)])
                booking_ids = [book.pr_booking_id.id for book in timeslot_booking_ids if book.pr_booking_id.booking_type in ['normal', 'sic'] and book.pr_booking_id.status not in ['cancelled', 'completed']]
                all_booked_ids = booking_ids + special_booking
                slot_wise_booking.update({match.id: all_booked_ids})

            #Check equipments are free for requested timeslot
            equipment_not_availbale = []
            if all_anchors and all_anchors[0] != 'sic_booking':
                for an in all_anchors:
                    equipment = self.env['anchor.size.type'].search(
                            [
                                ('anchor_type_id', '=', int(eval(an[1]))),
                                ('equipment_id', '!=', False),
                                ('anchor_size_ids', '=', int(eval(an[0])))
                            ],
                        limit=1)
                    if equipment:
                        reuired_equipment.append(equipment.equipment_id.id)
                reuired_equipment = list(set(reuired_equipment))
                for slow_wise in slot_wise_booking.keys():
                    temp_continue = 0
                    for eq in list(set(reuired_equipment)):
                        equipment = self.env['equipment.equipment'].browse([eq])
                        master_total_eq = equipment.qty
                        total_remaining = 0
                        used_eq = 0
                        for booking_order in slot_wise_booking[slow_wise]:
                            pr_book = self.env['project.booking'].browse([booking_order])
                            all_pr_eq = [an.equipment_id.id for an in pr_book.project_booking_anchor_ids if an.equipment_id and an.equipment_id.id]
                            for an in list(set(all_pr_eq)):
                                if an == eq:
                                    used_eq += 1
                        total_remaining = int(master_total_eq) - int(used_eq)
                        if total_remaining <= 0:
                            if slow_wise in match_timeslot_all_ids:
                                match_timeslot_all_ids.remove(slow_wise)
                                temp_continue = 1
                                equipment_not_availbale.append(slow_wise)
                    if temp_continue == 1:
                       continue
            # No one time slot is free
            if not match_timeslot_all_ids:
                return [slot_time]
            else:
                no_one_booking = []
                no_one_booking_tester = []
                slot_asssign = []
                for aaa in equipment_not_availbale:
                    del slot_wise_booking[int(aaa)]
                project_id_browse = self.env['project.project'].browse([int(project_id)])
                reserved_tester_free = {}
                if project_id_browse.tester_ids:
                    reserved_tester_list = [a.id for a in project_id_browse.tester_ids]
                    leaved_tester1 = []
                    for ts in reserved_tester_list:
                        all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                        if all_unavailbel:
                            for aa in all_unavailbel:
                                if aa.is_half_leave:
                                    remove_list = []
                                    local = pytz.timezone(self.env.user.tz)
                                    aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                    aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                    start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                    end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                    start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                    end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                    if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                        start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                        end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                        for tt in reserved_tester_list:
                                            time = self.env['time.slot.start.end'].sudo().browse([tt])
                                            if (float(start_time) <= float(time.timeslot_start_id.start_time) <= float(end_time)) or (float(start_time) <= float(time.timeslot_end_id.end_time) <= float(end_time)):
                                                remove_list.append(tt)
                                    if remove_list:
                                        for a in remove_list:
                                            leaved_tester1.append(a)
                                if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                    leaved_tester1.append(ts)
                    for slow_wise in slot_wise_booking.keys():
                        if not slot_wise_booking[slow_wise]:
                            no_one_booking.append(slow_wise)
                        for ts in project_id_browse.tester_ids:
                            if not no_one_booking_tester:
                                no_one_booking_tester.append(ts.id)
                            booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                            for lt in leaved_tester1:
                                booking_tester_ids.append(lt)
                            if booking_tester_ids and slow_wise not in slot_asssign:
                                if ts.id not in booking_tester_ids:
                                    if ts.id in reserved_tester_free.keys():
                                        slot_asssign.append(slow_wise)
                                        if type(reserved_tester_free.get(ts.id)) != list:
                                            all_val = [reserved_tester_free.get(ts.id), slow_wise]
                                            reserved_tester_free[ts.id] = list(set(all_val))
                                        else:
                                            all_val = reserved_tester_free.get(ts.id)
                                            all_val.append(slow_wise)
                                            reserved_tester_free[ts.id] = list(set(all_val))
                                    else:
                                        reserved_tester_free.update({ts.id: slow_wise})
                                        slot_asssign.append(slow_wise)
                    no_one_booking = list(set(no_one_booking))
                    if no_one_booking_tester and no_one_booking:
                        if reserved_tester_free and no_one_booking_tester[0] in reserved_tester_free.keys():
                            no_one_booking.append(reserved_tester_free[no_one_booking_tester[0]])
                            reserved_tester_free[no_one_booking_tester[0]] = no_one_booking
                        else:
                            reserved_tester_free.update({no_one_booking_tester[0]: no_one_booking})
                        no_one_booking_tester = []
                        no_one_booking = []
                # If no one reserved tester is available then
                for ts in reserved_tester_free.keys():
                    all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                    if all_unavailbel:
                        for aa in all_unavailbel:
                            if aa.is_half_leave:
                                remove_list = []
                                local = pytz.timezone(self.env.user.tz)
                                aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                    start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                    end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                    for am in reserved_tester_free[ts]:
                                        time = self.env['time.slot.start.end'].sudo().browse([am])
                                        if (float(start_time) <= float(time.timeslot_start_id.start_time) <= float(end_time)) or (float(start_time) <= float(time.timeslot_end_id.end_time) <= float(end_time)):
                                            remove_list.append(am)
                                if remove_list:
                                    for a in remove_list:
                                        reserved_tester_free[ts].remove(a)
                                if reserved_tester_free[ts] == []:
                                    del reserved_tester_free[ts]
                            if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                del reserved_tester_free[ts]
                if reserved_tester_free:
                    return reserved_tester_free
                if not reserved_tester_free:
                    sic_testers_free = {}
                    no_one_booking = []
                    slot_asssign = []
                    all_tester = self.env['res.partner'].search([('type_of_user', '=', 'hilti_tester')])
                    if str(sic) == 'yes':
                        all_sic_tester = []
                        if all_anchors and all_anchors[0] != 'sic_booking':
                            for tes in all_tester:
                                for pr in tes.project_ids:
                                    if pr.id == int(project_id):
                                        all_sic_tester.append(tes.id)
                            if not all_sic_tester:
                                return [slot_time]
                        else:
                            all_sic_tester = [a.id for a in all_tester]
                    else:
                        all_sic_tester = [a.id for a in all_tester]
                    for slow_wise in slot_wise_booking.keys():
                        booking_tester_ids_all = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                        for a in booking_tester_ids_all:
                            if a in all_sic_tester:
                                all_sic_tester.remove(a)
                    if all_sic_tester:
                        zone_ids = self.env['zone.zone'].search([])
                        testers_zone1 = []
                        for zone in zone_ids:
                            for postal in zone.postal_code_ids:
                                if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                    if testers_zone1:
                                        break
                                    else:
                                        testers_zone1.append(zone)
                        leaved_tester = []
                        for ts in all_sic_tester:
                            all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', ts)])
                            if all_unavailbel:
                                for aa in all_unavailbel:
                                    if aa.is_half_leave:
                                        remove_list = []
                                        local = pytz.timezone(self.env.user.tz)
                                        aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                        aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                        start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                        end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                        start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                        end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                        if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                            start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                            end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                            for tt in all_sic_tester:
                                                time = self.env['time.slot.start.end'].sudo().browse([tt])
                                                if (float(start_time) <= float(time.timeslot_start_id.start_time) <= float(end_time)) or (float(start_time) <= float(time.timeslot_end_id.end_time) <= float(end_time)):
                                                    remove_list.append(tt)
                                        if remove_list:
                                            for a in remove_list:
                                                leaved_tester.append(a)
                                    if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                        leaved_tester.append(ts)
                        all_tester = [a.id for tester in testers_zone1 for a in tester.tester_ids]
                        for slow_wise in slot_wise_booking.keys():
                            for ts in all_tester:
                                if not slot_wise_booking[slow_wise]:
                                    no_one_booking.append(slow_wise)
                                booking_tester_ids = [self.env['project.booking'].browse([booking_order]).tester_id.id for booking_order in slot_wise_booking[slow_wise] if booking_order]
                                for mad in leaved_tester:
                                    booking_tester_ids.append(mad)
                                if booking_tester_ids and slow_wise not in slot_asssign:
                                    if ts not in booking_tester_ids:
                                        if ts in sic_testers_free.keys():
                                            slot_asssign.append(slow_wise)
                                            if type(sic_testers_free.get(ts)) != list:
                                                all_val = [sic_testers_free.get(ts), slow_wise]
                                                sic_testers_free[ts] = list(set(all_val))
                                            else:
                                                all_val = sic_testers_free.get(ts)
                                                all_val.append(slow_wise)
                                                sic_testers_free[ts] = list(set(all_val))
                                        else:
                                            sic_testers_free.update({ts: slow_wise})
                                            slot_asssign.append(slow_wise)
                    no_one_booking = list(set(no_one_booking))
                    if not sic_testers_free and not no_one_booking:
                        return [slot_time]
                    else:
                        zone_ids = self.env['zone.zone'].search([])
                        testers_zone = []
                        tester_availble_in_zone = {}
                        for zone in zone_ids:
                            for postal in zone.postal_code_ids:
                                if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                    if testers_zone:
                                        break
                                    else:
                                        testers_zone.append(zone)
                        if testers_zone:
                            slot_allocate = []
                            no_one_booking_tester = []
                            for tester in testers_zone[0].tester_ids:
                                if tester.id in sic_testers_free.keys():
                                    if not sic_testers_free[tester.id] in slot_allocate:
                                        slot_allocate.append(sic_testers_free[tester.id])
                                        tester_availble_in_zone[tester.id] = sic_testers_free[tester.id]
                                        del sic_testers_free[tester.id]
                                if no_one_booking:
                                    tester_is_not_available = False
                                    if 'passed_tester_id' in self._context and self._context.get('passed_tester_id') in all_sic_tester:
                                        all_sic_tester.remove(self._context.get('passed_tester_id'))
                                    if tester.id in all_sic_tester and not no_one_booking_tester:
                                        all_unavailbel = self.env['my.request'].search([('req_type', '=', 'unavailability'), ('status', '=', 'approved'), ('partner_id', '=', tester.id)])
                                        if all_unavailbel:
                                            for aa in all_unavailbel:
                                                if aa.is_half_leave:
                                                    local = pytz.timezone(self.env.user.tz)
                                                    aastart_date = datetime.strptime(aa.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                                    aaend_date = datetime.strptime(aa.end_date, DEFAULT_SERVER_DATETIME_FORMAT)
                                                    start_datetime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                                    end_datetime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).date()
                                                    start_sstime = aastart_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                                    end_sstime = aaend_date.replace(tzinfo = pytz.utc).astimezone(local).time()
                                                    if (str(start_datetime) <= str(booking_date) <= str(end_datetime)):
                                                        start_time = "%02d.%02d" % (int(str(start_sstime).split(':')[0]), ((int(str(start_sstime).split(':')[1]) * 100) / 60))
                                                        end_time = "%02d.%02d" % (int(str(end_sstime).split(':')[0]), ((int(str(end_sstime).split(':')[1]) * 100) / 60))
                                                        for nn in no_one_booking:
                                                            time = self.env['time.slot.start.end'].sudo().browse(nn)
                                                            if (float(start_time) <= float(time.timeslot_start_id.start_time) <= float(end_time)) or (float(start_time) <= float(time.timeslot_end_id.end_time) <= float(end_time)):
                                                                tester_is_not_available = True
                                                if not aa.is_half_leave and (aa.full_start_date <= str(booking_date) <= aa.full_end_date):
                                                    tester_is_not_available = True
                                        if tester_is_not_available == False:
                                            no_one_booking_tester.append(tester.id)
                            if no_one_booking and no_one_booking_tester:
                                if 'passed_timeslot_id' in self._context:
                                    for an in self._context.get('passed_timeslot_id'):
                                        if an in tester_availble_in_zone.values():
                                            no_one_booking = []
                                if no_one_booking:
                                    if tester_availble_in_zone and no_one_booking_tester[0] in tester_availble_in_zone.keys():
                                        no_one_booking.append(tester_availble_in_zone[no_one_booking_tester[0]])
                                        tester_availble_in_zone[no_one_booking_tester[0]] = no_one_booking
                                    else:
                                        tester_availble_in_zone.update({no_one_booking_tester[0]: no_one_booking})
                                    no_one_booking = []
                                    no_one_booking_tester = []
                            if not sic_testers_free and not no_one_booking:
                                return tester_availble_in_zone
                                # I found all tester with timeslot ids and also search zone , in zone i found testers
                            else:
                                postal_nearest_zone = []
                                for zoone in testers_zone[0].seq_ids:
                                    for postal in zoone.postal_code_id:
                                        if postal.name == str(map(str,str(postal_code))[0] + map(str,str(postal_code))[1]):
                                            postal_nearest_zone = [aa for aa in zoone.zone_ids]
                                not_postal_code = False
                                if postal_nearest_zone:
                                    no_one_booking_tester = []
                                    slot_allocate_1 =[]
                                    for ne_tester in postal_nearest_zone:
                                        for tester in ne_tester.tester_ids:
                                            if tester.id in sic_testers_free.keys():
                                                if not sic_testers_free[tester.id] in slot_allocate_1:
                                                    slot_allocate_1.append(sic_testers_free[tester.id])
                                                    tester_availble_in_zone[tester.id] = sic_testers_free[tester.id]
                                                    del sic_testers_free[tester.id]
                                                    not_postal_code = True
                                            if no_one_booking:
                                                if tester.id in all_sic_tester and not no_one_booking_tester:
                                                    no_one_booking_tester.append(tester.id)
                                    if no_one_booking and no_one_booking_tester:
                                        if 'passed_timeslot_id' in self._context:
                                            for an in self._context.get('passed_timeslot_id'):
                                                if an in tester_availble_in_zone.values():
                                                    no_one_booking = []
                                        if no_one_booking:
                                            tester_availble_in_zone[no_one_booking_tester[0]] = no_one_booking
                                            no_one_booking = []
                                            no_one_booking_tester = []
                                            not_postal_code = True
                            return tester_availble_in_zone

    @api.multi
    def cancel_booking(self):
        if self._uid not in self.env.ref('hilti_modifier_accessrights.group_hilti_admin').users.ids:
            self.check_date("Cancellation of booking is not allowed after reconfirmation of booking. Please contact Hilti admin for further assistance.")
        self.sudo().write({'status': 'cancelled'})
        return True

    def final_booking_admin(self):
        self.is_final = True

    def check_date(self, msg=''):
        start_datetime = ''
        end_datetime = ''
        action_needed_before_hours = self.env['ir.values'].get_default('admin.configuration', 'action_needed_before_hours')
        if not self.env.user.tz:
            raise UserError(_('Please set the time zone by clciking on user name - Preferences - Time Zone.'))
        now = datetime.now(pytz.timezone(self.env.user.tz)).replace(tzinfo=None)
        if self.booking_type in ['normal', 'sic']:
            if not self.time_booking_ids:
                raise UserError(_('Start date time and End date time is not defined.'))
            start_time = self.time_booking_ids[0].timeslot_start_id.start_time
            end_time = self.time_booking_ids[0].timeslot_end_id.end_time
            start_datetime = datetime.strptime(self.time_booking_ids[0].booking_date + ' ' + ("%d:%02d:%02d" % (int(start_time), (start_time * 60) % 60, (start_time * 3600) % 60)), "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(self.time_booking_ids[0].booking_date + ' ' + ("%d:%02d:%02d" % (int(end_time), (end_time * 60) % 60, (end_time * 3600) % 60)), "%Y-%m-%d %H:%M:%S")
        else:
            start_datetime = datetime.strptime(self.start_date_time, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(self.end_date_time, "%Y-%m-%d %H:%M:%S")
        if now >= start_datetime:
            raise UserError(_("This booking's start date has already been passed."))

        if start_datetime <= (now + timedelta(hours=action_needed_before_hours)):
            raise UserError(_(msg))
        return True

    @api.onchange('partner_id')
    def onchange_partner_id_for_default(self):
        if self._context and 'booking_id_default' in self._context.keys():
            active_booking_id = self.search([('id', '=', self._context.get('booking_id_default'))])
            total_list = []
            for line in active_booking_id.project_booking_anchor_ids:
                anchor_dict = {'name': line.name, 'anchor_type_id': line.anchor_type_id and line.anchor_type_id.id or False,
                               'anchor_size_id': line.anchor_size_id and line.anchor_size_id.id or False, 'anchor_qty': line.anchor_qty,
                               'an_complexity': line.an_complexity}
                total_list.append(anchor_dict)
            if total_list:
                self.project_booking_anchor_ids = total_list



    @api.multi
    def rebook_booking(self):
        action = {}
        ctx = dict()
        form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_company', 'project_booking_view_admin_re_booking')[1]
        ctx.update({
            'default_booking_type': self.booking_type,
            'default_company_id': self.company_id and self.company_id.id or False,
            'default_project_id': self.project_id and self.project_id.id or False,
            'default_partner_id': self.partner_id and self.partner_id.id or False,
            'default_contact_id': self.contact_id,
            'default_contact_number': self.contact_number,
            'default_sid_required': self.sid_required,
            'default_location_id': self.location_id and self.location_id.id or False,
            'default_is_final': True,
            'booking_id_default': self.id,
            'come_from_default': 1,
            'default_create_date': str(datetime.now()),
        })
        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.booking',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,
        }
        return action
    
    @api.multi
    def book_for_delay(self):
        action = {}
        ctx = dict()
        form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_company', 'project_booking_view_tester_book_for_delay')[1]
        ctx.update({
            'default_booking_type': self.booking_type,
            'default_company_id': self.company_id and self.company_id.id or False,
            'default_project_id': self.project_id and self.project_id.id or False,
            'default_partner_id': self.partner_id and self.partner_id.id or False,
            'default_contact_id': self.contact_id,
            'default_contact_number': self.contact_number,
            'default_sid_required': self.sid_required,
            'default_location_id': self.location_id and self.location_id.id or False,
            'default_is_final': True,
            'booking_id_default': self.id,
            'come_from_default': 1,
            'send_remark_to_cust': 1,
            'default_create_date': str(datetime.now()),
        })
        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.booking',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,
        }
        return action
    
    def _send_notification_on_reject_by_tester(self, self_obj, rejected_obj):
        #TODO by mustafa
        # in this case just notifiy tester of another tester
        return True

    @api.multi
    def tester_reject_tester_swap_booking(self):
        # Reject swap tester booking
        for self_obj in self:
            # is_swap_req_sent
            if not self_obj.from_swap_booking_id:
                raise UserError(_('Rejection of this request is not possible as this request no longer exists. Thank You.'))
            
            self_obj.from_swap_booking_id.sudo().write({
            'is_swap_req_rejected': True,
            'is_swap_req_sent': False,
            'to_swap_req_booking_id': False,
            'from_swap_booking_id': False,
            })
            self._send_notification_on_reject_by_tester(self_obj, self_obj.from_swap_booking_id)
            self_obj.write({
                'is_swap_req_get': False,
                'from_swap_booking_id': False,
                'to_swap_req_booking_id': False,
            })
            
            #once all the things done then we will remove the requested id from each other
            #self_obj.from_swap_booking_id.sudo().write({'is_swap_req_rejected': True})
        return True
    
    def _send_notification_on_accept_by_tester(self, booking_to_obj, booking_from_obj):
        #TODO by mustafa
        # in this case notify both customer and tester
        # Pls ask Valli for msg format
        return True
    
    @api.multi
    def tester_accept_tester_swap_booking(self):
        # Accept tester request
        # if it get accepted by tester then swap tester with each other
        for self_obj in self:
            if not self_obj.from_swap_booking_id:
                raise UserError(_('Rejection of this request is not possible as this request no longer exists. Thank You.'))
            if not self_obj.user_tester_id:
                raise UserError(_('No tester found in %s.' %(self_obj.booking_no)))
            if self_obj.from_swap_booking_id and not self_obj.from_swap_booking_id.user_tester_id:
                raise UserError(_('No tester found in %s.' %(self_obj.from_swap_booking_id.booking_no)))
            # this tester id contains from where we get request this use for write in current self_obj  
            from_swap_tester_id = self_obj.from_swap_booking_id.user_tester_id
            # to swap id is contains self_obj's tester which we will use to write in from swap id
            to_swap_tester_id = self_obj.user_tester_id
            
            self_obj.sudo().write({
                            'user_tester_id': from_swap_tester_id.id,
                            'is_swap_req_get': False,
                            })
            self._send_notification_on_accept_by_tester(self_obj, self_obj.from_swap_booking_id)
            self_obj.from_swap_booking_id.sudo().write({
                'user_tester_id': to_swap_tester_id.id,
                'is_swap_req_accepted': True,
                'is_swap_req_sent': False,
            })
            
        return True

    @api.multi
    def reschedule_booking(self):
        action_needed_before_hours = self.env['ir.values'].get_default('admin.configuration', 'action_needed_before_hours')
        self.check_date("This booking cannot be rescheduled now due to the booking reschedule restriction before " + str(action_needed_before_hours) + " hours of booking.")
        action = {}
        ctx = dict()
        if self.booking_type in ['normal', 'sic']:
            time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
            if time_slot.time_slot_based:
                form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_customer_booking', 'time_slot_booking_view_dynamic_view')[1]
            else:
                form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_customer_booking', 'time_slot_booking_view')[1]
            ctx.update({
                'is_reschedule': True,
                'default_pr_booking_id': self.id,
                'pr_booking_type_reschedule': self.booking_type
            })
            action = {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'timeslot.booking',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
                'context': ctx,
            }
        else:
            form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_customer_booking', 'reschedule_booking_form_view')[1]
            ctx.update({
                'booking_type': self.booking_type,
                'default_booking_type': self.booking_type
            })
            action = {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'reschedule.booking',
                'views': [(form_id, 'form')],
                'view_id': form_id,
                'target': 'new',
                'context': ctx,
            }
        return action

    def reassign_tester_from_admin(self):
        local = pytz.timezone(self.env.user.tz)
        if not self.final_start_dtime or not self.final_end_dtime:
            raise Warning(_("Re-assigning Testers is not possible as the date and time does not exist for this booking."))
        check_dt_start = datetime.strptime(self.final_start_dtime, "%Y-%m-%d %H:%M:%S")
        start_date = pytz.utc.localize(check_dt_start, is_dst=None).astimezone(local).date()
        start_time_formate = pytz.utc.localize(check_dt_start, is_dst=None).astimezone(local).time()
        start_time = start_time_formate.hour+start_time_formate.minute/60.0
        check_dt_end = datetime.strptime(self.final_end_dtime, "%Y-%m-%d %H:%M:%S")
        end_date = pytz.utc.localize(check_dt_end, is_dst=None).astimezone(local).date()
        end_time_formate = pytz.utc.localize(check_dt_end, is_dst=None).astimezone(local).time()
        end_time = end_time_formate.hour+end_time_formate.minute/60.0
        total_hours = []
        all_anchors = []
        for an in self.project_booking_anchor_ids:
            type_an = self.env['anchor.master'].search([('anchor_type_id','=', an.anchor_type_id and an.anchor_type_id.id)])
            if an.an_complexity == 'complex':
                total_hours.append(str(float(type_an.complex_time) * float(an.anchor_qty)).decode('utf-8'))
            if an.an_complexity == 'simple':
                total_hours.append(str(float(type_an.simple_time) * float(an.anchor_qty)).decode('utf-8'))
            if an.an_complexity == 'medium':
                total_hours.append(str(float(type_an.medium_time) * float(an.anchor_qty)).decode('utf-8'))
        if self.sid_required == False:
            sic = 'no'
        else:
            sic = 'yes'
        if self.booking_type == 'special':
            booking_logic = self.sudo().dedicated_booking_logic(start_date, start_time, end_date, end_time,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name)
            if booking_logic:
                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
                self.user_tester_id = tester_id and tester_id.id or False
            else:
                raise Warning(_("Testers are not available for re-assignment of bookings. Please enable the re-assign tester manually option."))
#         if self.booking_type == 'sic':
#             booking_logic = self.sudo().sic_booking_logic(start_date,start_time,end_time,self.postal_code.name)
#             if booking_logic:
#                 tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
#                 self.user_tester_id = tester_id and tester_id.id or False
#                 if self._context and 'from_application' in self._context:
#                     return 'tester_assign'
#             else:
#                 if self._context and 'from_application' in self._context:
#                     return 'tester_not_free'
#                 raise Warning(_("No one tester is free please select another datetime."))
        if self.booking_type in ['normal', 'sic']:
            if self.booking_type == 'sic':
                total_hours = [str(float(self.sic_required_hours)).decode('utf-8')]
                all_anchors = []
            time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
            if time_slot.time_slot_based:
                start = False
                end = False
                for aa in self.time_booking_ids:
                    if not start:
                        start = aa.timeslot_start_id.start_time
                    end = aa.timeslot_end_id.end_time
                if self.tester_id and self.tester_id.id:
                    tester_id_passed = self.tester_id.id
                else:
                    tester_id_passed = False
                booking_logic = self.sudo().with_context(passed_timeslot_id = [start, end], passed_tester_id = tester_id_passed).booking_logic_dynamic(start_date,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name, False)
                def call_booking_order_reassign(booking_logic):
                    booking_logic = self.sudo().with_context(passed_timeslot_id = [start, end], passed_tester_id = tester_id_passed).booking_logic_dynamic(start_date,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.sudo().with_context(passed_timeslot_id = [start, end], passed_tester_id = tester_id_passed).booking_logic_dynamic(start_date,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order_reassign(booking_logic)
                    if booking_logic and booking_logic[0] == False:
                        raise Warning(_("Testers are not available for re-assignment of bookings. Please enable the re-assign tester manually option."))
                if type(booking_logic) != list and type(booking_logic) == dict:
                    time_slot_id = []
                    done = False
                    for slot_book in booking_logic.keys():
                        slot_book_value = []
                        for aa in booking_logic[slot_book]:
                            if type(aa) != list:
                                slot_book_value.append(booking_logic[slot_book])
                                break
                            else:
                                slot_book_value = booking_logic[slot_book]
                                break
                        for time1 in slot_book_value:
                            if time1 == [start_time, end_time]:
                                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(slot_book))])
                                self.user_tester_id = tester_id and tester_id.id or False
                                done = True
                                if self._context and 'from_application' in self._context:
                                    return 'tester_assign'
                    if done == False:
                        if self._context and 'from_application' in self._context:
                            return 'tester_not_free'
                        raise Warning(_("No one other tester is free for this time, Please select ."))
            else:
                passed_timeslot_id = [a.time_slot_id.id for a in self.time_booking_ids if a.time_slot_id and a.time_slot_id.id]
                if self.tester_id and self.tester_id.id:
                    tester_id_passed = self.tester_id.id
                else:
                    tester_id_passed = False
                booking_logic = self.with_context(passed_timeslot_id = passed_timeslot_id, passed_tester_id = tester_id_passed).booking_logic(start_date,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name, False)
                def call_booking_order_static(booking_logic):
                    booking_logic = self.with_context(passed_timeslot_id = passed_timeslot_id, passed_tester_id = tester_id_passed).booking_logic(start_date,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name, booking_logic[0])
                    if type(booking_logic) == list:
                        if booking_logic and booking_logic[0] != False:
                            booking_logic = self.with_context(passed_timeslot_id = passed_timeslot_id, passed_tester_id = tester_id_passed).booking_logic(start_date,total_hours, all_anchors, self.project_id.id, sic, self.postal_code.name, booking_logic[0])
    #                         booking_logic = call_booking_order(booking_logic)
                    return booking_logic
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = call_booking_order_static(booking_logic)
                    elif booking_logic and booking_logic[0] == False:
                        raise Warning(_("Testers are not available for re-assignment of bookings. Please enable the re-assign tester manually option."))
                remaining_slot = []
                if type(booking_logic) != list and type(booking_logic) == dict:
                    done = False
                    for slot_book in booking_logic.keys():
                        if type(booking_logic[slot_book]) != list:
                            slot_book_value = [booking_logic[slot_book]]
                        else:
                            slot_book_value = booking_logic[slot_book]
                        for nn in slot_book_value:
                            use_slot_id = False
                            slot_id = self.env['time.slot.start.end'].search([('id', '=', nn)])
                            for ab in self.time_booking_ids:
                                if slot_id == ab.time_slot_id:
                                    tester_id = self.env['res.users'].sudo().search([('partner_id', '=', slot_book)])
                                    self.user_tester_id = tester_id and tester_id.id or False
                                    done = True
                                    if self._context and 'from_application' in self._context:
                                        return 'tester_assign'
                    if done == False:
                        if self._context and 'from_application' in self._context:
                            return 'tester_not_free'
                        raise Warning(_("Testers are not available for re-assignment of bookings. Please enable the re-assign tester manually option."))


    @api.multi
    def reconfirm_booking_from_application(self):
        action_needed_before_hours = self.env['ir.values'].get_default('admin.configuration', 'action_needed_before_hours')
        self.check_date("This booking cannot be rescheduled now due to the booking reschedule restriction before " + str(action_needed_before_hours) + " hours of booking.")
        self.status = 'reconfirmed'
        return True

    @api.multi
    def reconfirm_booking(self):
        action_needed_before_hours = self.env['ir.values'].get_default('admin.configuration', 'action_needed_before_hours')
        self.check_date("This booking cannot be rescheduled now due to the booking reschedule restriction before " + str(action_needed_before_hours) + " hours of booking.")
        compose_form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_customer_booking', 'reconfirm_booking_form_view')[1]
        ctx = dict()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reconfirm.booking',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def start_testing(self):
        for rec in self:
            rec.testing_start_time = datetime.today()
            rec.status = 'started'
        return {'testing_start_time': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}

    @api.multi
    def stop_testing(self):
        res = {'testing_end_time': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT), 'testing_start_time': self.testing_start_time}
#         for rec in self:
        self.testing_end_time = datetime.today()
        if self.testing_start_time and self.testing_end_time:
            diff = datetime.strptime(self.testing_start_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(self.testing_end_time, "%Y-%m-%d %H:%M:%S")
            total_hm = abs(diff)
            self.testing_duretion = total_hm
            res.update({
                'testing_duretion': total_hm.total_seconds() / 60
            })
        return res

    @api.model
    def dedicated_bookings_for_mobile(self):
        records = self.search_read([('add_accept_button', '=', True), ('status', '!=', 'cancelled')], ['booking_no', 'final_start_dtime', 'final_end_dtime', 'project_id', 'sid_required', 'user_tester_id', 'project_booking_anchor_ids', 'location_id', 'postal_code', 'status', 'contact_id', 'contact_number', 'booking_type', 'company_id', 'partner_id', 'tester_phone'])
        for record in records:
            if record.get('project_booking_anchor_ids'):
                record['project_booking_anchor_ids'] = self.env['project.booking.anchor'].search_read([('id', 'in', record.get('project_booking_anchor_ids'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity', 'equipment_id'])
        return records
    
    @api.model
    def all_task_for_mobile(self, days='all'):
        domain = [('status', 'in', ['pending', 'reconfirmed']),('user_tester_id', '!=', self._uid)]
        if days != 'all':
            days = int(days)
            current_date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
            x_days_after_datetime = datetime.strftime(datetime.combine((datetime.now() + timedelta(days=days)), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
            domain.append(('final_start_dtime', '>=', current_date))
            domain.append(('final_start_dtime', '<=', x_days_after_datetime))
        records = self.search_read(domain, ['booking_no', 'final_start_dtime', 'final_end_dtime', 'project_id', 'sid_required', 'user_tester_id', 'project_booking_anchor_ids', 'location_id', 'postal_code', 'status', 'contact_id', 'contact_number', 'booking_type', 'company_id', 'partner_id', 'tester_phone'])
        for record in records:
            if record.get('project_booking_anchor_ids'):
                record['project_booking_anchor_ids'] = self.env['project.booking.anchor'].search_read([('id', 'in', record.get('project_booking_anchor_ids'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity', 'equipment_id'])
        return records

    @api.model
    def search_browse(self, domain, fields):
        query = self._where_calc(domain)
        from_clause, where_clause, where_clause_params = query.get_sql()
        query_str = 'SELECT %s FROM ' % ",".join(fields) + from_clause + (where_clause and (" WHERE %s" % where_clause) or '')
        self._cr.execute(query_str, where_clause_params)
        return self._cr.dictfetchall()

    @api.model
    def booking_mobile_dashboard(self, days='all', completed_bookings_fields=[], fields=[]):
        domain = []
        if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
            domain.append(('user_tester_id', '=', self._uid))
        if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
            domain.append(('user_id', '=', self._uid))
        booking_completed_domain = domain + [('status', '=', 'completed')]
        booking_pending_domain = domain + [('status', 'in', ['pending', 'started', 'reconfirmed', 'rescheduled'])]
        booking_reconfirm_domain = domain + [('status', 'in', ['reconfirmed'])]
        notification_domain = [('user_ids', '=', self._uid)]
        if days != 'all':
            days = int(days)
            current_date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
            x_days_before_datetime = datetime.strftime(datetime.combine((datetime.now() - timedelta(days=days)), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
            booking_completed_domain.append(('final_start_dtime', '<=', current_date))
            booking_completed_domain.append(('final_start_dtime', '>=', x_days_before_datetime))
            booking_pending_domain.append(('final_start_dtime', '<=', current_date))
            booking_pending_domain.append(('final_start_dtime', '>=', x_days_before_datetime))
            booking_reconfirm_domain.append(('final_start_dtime', '<=', current_date))
            booking_reconfirm_domain.append(('final_start_dtime', '>=', x_days_before_datetime))
            notification_domain.append(('create_date', '<=', current_date))
            notification_domain.append(('create_date', '>=', x_days_before_datetime))
        fields += ['id', 'booking_no', 'final_start_dtime', 'final_end_dtime', 'project_id', 'sid_required', 'user_tester_id', 'location_id', 'postal_code', 'status', 'contact_id', 'contact_number', 'booking_type', 'company_id', 'partner_id', 'tester_phone', 'is_swap_req_get', 'is_swap_req_sent', 'is_swap_req_accepted', 'is_swap_req_rejected', 'from_swap_booking_id', 'to_swap_req_booking_id', 'testing_end_time', 'testing_start_time']
        completed_bookings_fields += ['id', 'booking_no', 'final_start_dtime', 'final_end_dtime', 'project_id', 'sid_required', 'user_tester_id', 'location_id', 'postal_code', 'status', 'contact_id', 'contact_number', 'booking_type', 'company_id', 'partner_id', 'tester_phone', 'testing_remark', 'testing_end_time', 'testing_start_time']

        completed_bookings = self.search_browse(booking_completed_domain, completed_bookings_fields) 
        pending_bookings = self.search_browse(booking_pending_domain, fields)
        reconfirm_bookings = self.search_browse(booking_reconfirm_domain, fields)
        notifications = self.env['notification.notification'].search_browse(notification_domain, ['notification_no', 'name'])
        
        for pending_rec in pending_bookings:
            pending_rec = remove_none(pending_rec)
            
            if 'booking_type' in pending_rec:
                if pending_rec.get('booking_type') == 'normal':
                    pending_rec['booking_type'] = "Normal Booking"
                if pending_rec.get('booking_type') == 'special':
                    pending_rec['booking_type'] = "Dedicated Support Booking"
                if pending_rec.get('booking_type') == 'sic':
                    pending_rec['booking_type'] = "SIC Booking"
            
            if pending_rec.get('project_id'):
                self._cr.execute("select p.id, a.name from project_project as p, account_analytic_account as a where p.analytic_account_id = a.id and p.id = %s" % pending_rec.get('project_id'))
                pending_rec['project_id'] = self._cr.fetchone()
            if pending_rec.get('user_tester_id'):
                self._cr.execute("select res_users.id, res_partner.name from res_partner, res_users where res_users.partner_id = res_partner.id and res_users.id = %s" % pending_rec.get('user_tester_id'))
                pending_rec['user_tester_id'] = self._cr.fetchone()
            if pending_rec.get('location_id'):
                pending_rec['location_id'] = self.env['location.location'].search_browse([('id', '=', pending_rec.get('location_id'))], ['id', 'address'])[0].values()
            if pending_rec.get('postal_code'):
                pending_rec['postal_code'] = self.env['postal.code'].search_browse([('id', '=', pending_rec.get('postal_code'))], ['id', 'name'])[0].values()
            if pending_rec.get('company_id'):
                pending_rec['company_id'] = self.env['res.partner'].search_browse([('id', '=', pending_rec.get('company_id'))], ['id', 'name'])[0].values()
            if pending_rec.get('partner_id'):
                pending_rec['partner_id'] = self.env['res.partner'].search_browse([('id', '=', pending_rec.get('partner_id'))], ['id', 'name'])[0].values()
            
            project_booking_anchors = self.env['project.booking.anchor'].search_browse([('project_booking_id', '=', pending_rec.get('id'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity', 'equipment_id'])
            for project_booking_anchor in project_booking_anchors:
                project_booking_anchor = remove_none(project_booking_anchor)
                if project_booking_anchor.get('anchor_type_id'):
                    project_booking_anchor['anchor_type_id'] = self.env['anchor.type'].search_browse([('id', '=', project_booking_anchor.get('anchor_type_id'))], ['id', 'name'])[0].values()
                if project_booking_anchor.get('equipment_id'):
                    project_booking_anchor['equipment_id'] = self.env['equipment.equipment'].search_browse([('id', '=', project_booking_anchor.get('equipment_id'))], ['id', 'name'])[0].values()
                if project_booking_anchor.get('anchor_size_id'):
                    project_booking_anchor['anchor_size_id'] = self.env['anchor.size'].search_browse([('id', '=', project_booking_anchor.get('anchor_size_id'))], ['id', 'name'])[0].values()
            pending_rec['project_booking_anchor_ids'] = project_booking_anchors
          
        for reconfirm_rec in reconfirm_bookings:
            reconfirm_rec = remove_none(reconfirm_rec)
            
            if 'booking_type' in reconfirm_rec:
                if reconfirm_rec.get('booking_type') == 'normal':
                    reconfirm_rec['booking_type'] = "Normal Booking"
                if reconfirm_rec.get('booking_type') == 'special':
                    reconfirm_rec['booking_type'] = "Dedicated Support Booking"
                if reconfirm_rec.get('booking_type') == 'sic':
                    reconfirm_rec['booking_type'] = "SIC Booking"
            
            if reconfirm_rec.get('project_id'):
                self._cr.execute("select p.id, a.name from project_project as p, account_analytic_account as a where p.analytic_account_id = a.id and p.id = %s" % reconfirm_rec.get('project_id'))
                reconfirm_rec['project_id'] = self._cr.fetchone()
            if reconfirm_rec.get('user_tester_id'):
                self._cr.execute("select res_users.id, res_partner.name from res_partner, res_users where res_users.partner_id = res_partner.id and res_users.id = %s" % reconfirm_rec.get('user_tester_id'))
                reconfirm_rec['user_tester_id'] = self._cr.fetchone()
            if reconfirm_rec.get('location_id'):
                reconfirm_rec['location_id'] = self.env['location.location'].search_browse([('id', '=', reconfirm_rec.get('location_id'))], ['id', 'address'])[0].values()
            if reconfirm_rec.get('postal_code'):
                reconfirm_rec['postal_code'] = self.env['postal.code'].search_browse([('id', '=', reconfirm_rec.get('postal_code'))], ['id', 'name'])[0].values()
            if reconfirm_rec.get('company_id'):
                reconfirm_rec['company_id'] = self.env['res.partner'].search_browse([('id', '=', reconfirm_rec.get('company_id'))], ['id', 'name'])[0].values()
            if reconfirm_rec.get('partner_id'):
                reconfirm_rec['partner_id'] = self.env['res.partner'].search_browse([('id', '=', reconfirm_rec.get('partner_id'))], ['id', 'name'])[0].values()
            
            project_booking_anchors = self.env['project.booking.anchor'].search_browse([('project_booking_id', '=', reconfirm_rec.get('id'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity', 'equipment_id'])
            for project_booking_anchor in project_booking_anchors:
                project_booking_anchor = remove_none(project_booking_anchor)
                if project_booking_anchor.get('anchor_type_id'):
                    project_booking_anchor['anchor_type_id'] = self.env['anchor.type'].search_browse([('id', '=', project_booking_anchor.get('anchor_type_id'))], ['id', 'name'])[0].values()
                if project_booking_anchor.get('equipment_id'):
                    project_booking_anchor['equipment_id'] = self.env['equipment.equipment'].search_browse([('id', '=', project_booking_anchor.get('equipment_id'))], ['id', 'name'])[0].values()
                if project_booking_anchor.get('anchor_size_id'):
                    project_booking_anchor['anchor_size_id'] = self.env['anchor.size'].search_browse([('id', '=', project_booking_anchor.get('anchor_size_id'))], ['id', 'name'])[0].values()
                
                
                
            reconfirm_rec['project_booking_anchor_ids'] = project_booking_anchors

        for completed_rec in completed_bookings:
            completed_rec = remove_none(completed_rec)
            
            if 'booking_type' in completed_rec:
                if completed_rec.get('booking_type') == 'normal':
                    completed_rec['booking_type'] = "Normal Booking"
                if completed_rec.get('booking_type') == 'special':
                    completed_rec['booking_type'] = "Dedicated Support Booking"
                if completed_rec.get('booking_type') == 'sic':
                    completed_rec['booking_type'] = "SIC Booking"
            
            if completed_rec.get('project_id'):
                self._cr.execute("select p.id, a.name from project_project as p, account_analytic_account as a where p.analytic_account_id = a.id and p.id = %s" % completed_rec.get('project_id'))
                completed_rec['project_id'] = self._cr.fetchone()
            if completed_rec.get('user_tester_id'):
                self._cr.execute("select res_users.id, res_partner.name from res_partner, res_users where res_users.partner_id = res_partner.id and res_users.id = %s" % completed_rec.get('user_tester_id'))
                completed_rec['user_tester_id'] = self._cr.fetchone()
            if completed_rec.get('location_id'):
                completed_rec['location_id'] = self.env['location.location'].search_browse([('id', '=', completed_rec.get('location_id'))], ['id', 'address'])[0].values()
            if completed_rec.get('postal_code'):
                completed_rec['postal_code'] = self.env['postal.code'].search_browse([('id', '=', completed_rec.get('postal_code'))], ['id', 'name'])[0].values()
            if completed_rec.get('company_id'):
                completed_rec['company_id'] = self.env['res.partner'].search_browse([('id', '=', completed_rec.get('company_id'))], ['id', 'name'])[0].values()
            if completed_rec.get('partner_id'):
                completed_rec['partner_id'] = self.env['res.partner'].search_browse([('id', '=', completed_rec.get('partner_id'))], ['id', 'name'])[0].values()
            
            project_booking_anchors = self.env['project.booking.anchor'].search_browse([('project_booking_id', '=', completed_rec.get('id'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity', 'equipment_id'])
            for project_booking_anchor in project_booking_anchors:
                project_booking_anchor = remove_none(project_booking_anchor)
                if project_booking_anchor.get('anchor_type_id'):
                    project_booking_anchor['anchor_type_id'] = self.env['anchor.type'].search_browse([('id', '=', project_booking_anchor.get('anchor_type_id'))], ['id', 'name'])[0].values()
                if project_booking_anchor.get('equipment_id'):
                    project_booking_anchor['equipment_id'] = self.env['equipment.equipment'].search_browse([('id', '=', project_booking_anchor.get('equipment_id'))], ['id', 'name'])[0].values()
                if project_booking_anchor.get('anchor_size_id'):
                    project_booking_anchor['anchor_size_id'] = self.env['anchor.size'].search_browse([('id', '=', project_booking_anchor.get('anchor_size_id'))], ['id', 'name'])[0].values()
            completed_rec['project_booking_anchor_ids'] = project_booking_anchors
            
            project_booking_anchors = self.env['project.booking.anchor'].search_browse([('feed_project_booking_id', '=', completed_rec.get('id'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity', 'equipment_id', 'failer_qty'])
            for project_booking_anchor in project_booking_anchors:
                project_booking_anchor = remove_none(project_booking_anchor)
            completed_rec['feedback_anchor_ids'] = project_booking_anchors

        for notification in notifications:
            notification = remove_none(notification)
        return {
            'completed_bookings': {'length': len(completed_bookings), 'data': completed_bookings},
            'pending_bookings': {'length': len(pending_bookings), 'data': pending_bookings},
            'reconfirm_bookings': {'length': len(reconfirm_bookings), 'data': reconfirm_bookings},
            'notifications': {'length': len(notifications), 'data': notifications},
            'reminder': {'length': 0, 'ids': []},
         }


#     @api.model
#     def booking_mobile_dashboard(self, days='all', tester=False, customer=False):
#         domain = []
#         if tester:
#             domain.append(('user_tester_id', '=', self._uid))
#         if customer:
#             domain.append(('user_id', '=', self._uid))
#         booking_completed_domain = domain + [('status', '=', 'completed')]
#         booking_pending_domain = domain + [('status', '=', 'pending')]
#         notification_domain = [('user_ids', '=', self._uid)]
#         if days != 'all':
#             days = int(days)
#             current_date = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
#             x_days_before_datetime = datetime.strftime(datetime.combine((datetime.now() - timedelta(days=days)), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
#             booking_completed_domain.append(('final_start_dtime', '<=', current_date))
#             booking_completed_domain.append(('final_start_dtime', '>=', x_days_before_datetime))
#             booking_pending_domain.append(('final_start_dtime', '<=', current_date))
#             booking_pending_domain.append(('final_start_dtime', '>=', x_days_before_datetime))
#             notification_domain.append(('create_date', '<=', current_date))
#             notification_domain.append(('create_date', '>=', x_days_before_datetime))
#         fields = ['booking_no', 'final_start_dtime', 'project_id', 'sid_required', 'user_tester_id', 'project_booking_anchor_ids', 'location_id', 'postal_code', 'status', 'contact_id', 'contact_number', 'booking_type']
#         completed_bookings = self.search_read(booking_completed_domain, fields)
#         pending_bookings = self.search_read(booking_pending_domain, fields)
#         notifications = self.env['notification.notification'].search_read(notification_domain)
#
#         for pending_rec in pending_bookings:
#             if pending_rec.get('project_booking_anchor_ids'):
#                 project_booking_anchor = self.env['project.booking.anchor'].search_read([('id', 'in', pending_rec.get('project_booking_anchor_ids'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity'])
#                 pending_rec['project_booking_anchor_ids'] = project_booking_anchor
#
#         for completed_rec in completed_bookings:
#             if completed_rec.get('project_booking_anchor_ids'):
#                 project_booking_anchor = self.env['project.booking.anchor'].search_read([('id', 'in', completed_rec.get('project_booking_anchor_ids'))], ['name', 'anchor_type_id', 'anchor_size_id', 'anchor_qty', 'an_complexity'])
#                 completed_rec['project_booking_anchor_ids'] = project_booking_anchor
#
#         return {
#             'completed_bookings': {'length': len(completed_bookings), 'data': completed_bookings},
#             'pending_bookings': {'length': len(pending_bookings), 'data': pending_bookings},
#             'notifications': {'length': len(notifications), 'data': notifications},
#             'reminder': {'length': 0, 'ids': []},
#          }

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

        x_days_after_datetime, day_start, day_end, this_month_start_date, this_month_end_date, lastMonth_first_day, lastMonth_last_day = self.dates_for_domain()

        if 'today_delayed_bookings' in self._context and self._context.get('today_delayed_bookings'):
            query = "select id from project_booking where (final_start_dtime < testing_start_time or final_end_dtime < testing_end_time) and final_start_dtime >= '" + day_start + "' and final_start_dtime <= '" + day_end + "'"
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
                query += (' and user_id=' + str(self._uid))
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
                query += (' and user_tester_id=' + str(self._uid))
            self._cr.execute(query)
            return self.browse([r[0] for r in self._cr.fetchall()])

        if 'this_month_pending_bookings' in self._context and self._context.get('this_month_pending_bookings'):
            args += [('final_start_dtime', '<=', this_month_end_date), ('final_start_dtime', '>=', this_month_start_date), ('status', '=', 'pending')]
        if 'this_month_completed_bookings' in self._context and self._context.get('this_month_completed_bookings'):
            args += [('final_start_dtime', '<=', this_month_end_date), ('final_start_dtime', '>=', this_month_start_date), ('status', '=', 'completed')]
        if 'this_month_delayed_bookings' in self._context and self._context.get('this_month_delayed_bookings'):
            query = "select id from project_booking where (final_start_dtime < testing_start_time or final_end_dtime < testing_end_time) and final_start_dtime >= '" + this_month_start_date + "' and final_start_dtime <= '" + this_month_end_date + "'"
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
                query += (' and user_id=' + str(self._uid))
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
                query += (' and user_tester_id=' + str(self._uid))
            self._cr.execute(query)
            return self.browse([r[0] for r in self._cr.fetchall()])

        if 'last_month_pending_bookings' in self._context and self._context.get('last_month_pending_bookings'):
            args += [('final_start_dtime', '<=', lastMonth_last_day), ('final_start_dtime', '>=', lastMonth_first_day), ('status', '=', 'pending')]
        if 'last_month_completed_bookings' in self._context and self._context.get('last_month_completed_bookings'):
            args += [('final_start_dtime', '<=', lastMonth_last_day), ('final_start_dtime', '>=', lastMonth_first_day), ('status', '=', 'completed')]
        if 'last_month_delayed_bookings' in self._context and self._context.get('last_month_delayed_bookings'):
            query = "select id from project_booking where (final_start_dtime < testing_start_time or final_end_dtime < testing_end_time) and final_start_dtime >= '" + lastMonth_first_day + "' and final_start_dtime <= '" + lastMonth_last_day + "'"
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
                query += (' and user_id=' + str(self._uid))
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
                query += (' and user_tester_id=' + str(self._uid))
            self._cr.execute(query)
            return self.browse([r[0] for r in self._cr.fetchall()])

        if 'delayed_start' in self._context and self._context.get('delayed_start'):
            query = "select id from project_booking where final_start_dtime < testing_start_time"
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
                query += (' and user_id=' + str(self._uid))
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
                query += (' and user_tester_id=' + str(self._uid))
            self._cr.execute(query)
            return self.browse([r[0] for r in self._cr.fetchall()])

        if 'delayed_end' in self._context and self._context.get('delayed_end'):
            query = "select id from project_booking where final_end_dtime < testing_end_time"
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
                query += (' and user_id=' + str(self._uid))
            if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
                query += (' and user_tester_id=' + str(self._uid))
            self._cr.execute(query)
            return self.browse([r[0] for r in self._cr.fetchall()])

        return super(project_booking, self).search(args, offset, limit, order, count=count)

    def dates_for_domain(self):
        x_days_after_datetime = datetime.strftime(datetime.combine((datetime.now() + timedelta(days=7)), time.max), DEFAULT_SERVER_DATETIME_FORMAT)
        day_start = datetime.strftime(datetime.combine((datetime.now()), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
        day_end = datetime.strftime(datetime.combine((datetime.now()), time.max), DEFAULT_SERVER_DATETIME_FORMAT)

        current_date = date.today()
        this_month_start_date = datetime.strftime(datetime.combine(datetime(current_date.year, current_date.month, 1), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
        this_month_end_date = datetime.strftime(datetime.combine(datetime(current_date.year, current_date.month, calendar.mdays[current_date.month]), time.max), DEFAULT_SERVER_DATETIME_FORMAT)

        lastMonth_last_day = date.today().replace(day=1) - timedelta(days=1)
        lastMonth_first_day = datetime.strftime(datetime.combine(lastMonth_last_day.replace(day=1), time.min), DEFAULT_SERVER_DATETIME_FORMAT)
        lastMonth_last_day = datetime.strftime(datetime.combine(lastMonth_last_day, time.max), DEFAULT_SERVER_DATETIME_FORMAT)

        return x_days_after_datetime, day_start, day_end, this_month_start_date, this_month_end_date, lastMonth_first_day, lastMonth_last_day

    @api.model
    def retrieve_booking_dashboard(self):
        x_days_after_datetime, day_start, day_end, this_month_start_date, this_month_end_date, lastMonth_first_day, lastMonth_last_day = self.dates_for_domain()

        domain = []
        if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_customer'):
            domain.append(('user_id', '=', self._uid))
            domain.append(('is_final', '=', True))
        if self.env.user.has_group('hilti_modifier_accessrights.group_hilti_tester'):
            domain.append(('user_tester_id', '=', self._uid))

        today_booking_domain = domain + [('final_start_dtime', '>=', day_start), ('final_start_dtime', '<=', day_end)]
        x_days_booking_domain = domain + [('final_start_dtime', '<=', x_days_after_datetime), ('final_start_dtime', '>=', day_start)]
        today_pending_domain = today_booking_domain + [('status', '=', 'pending')]
        today_completed_domain = today_booking_domain + [('status', '=', 'completed')]

        today_booking = len(self.search(today_booking_domain).ids)
        x_days_booking = len(self.search(x_days_booking_domain).ids)

        today_pending_booking = len(self.search(today_pending_domain).ids)
        today_completed_booking = len(self.search(today_completed_domain).ids)
        today_delayed_booking = len(self.with_context(today_delayed_bookings=True).search(domain).ids)

        this_pending_month_booking = len(self.with_context(this_month_pending_bookings=True).search(domain).ids)
        this_completed_month_booking = len(self.with_context(this_month_completed_bookings=True).search(domain).ids)
        this_delayed_month_booking = len(self.with_context(this_month_delayed_bookings=True).search(domain).ids)

        last_pending_month_booking = len(self.with_context(last_month_pending_bookings=True).search(domain).ids)
        last_completed_month_booking = len(self.with_context(last_month_completed_bookings=True).search(domain).ids)
        last_delayed_month_booking = len(self.with_context(last_month_delayed_bookings=True).search(domain).ids)

        return {
            'bookings': {
                'today': today_booking,
                'next_7_days': x_days_booking,
            },
            'requests': {
                'today': 0,
                'next_7_days': 0,
            },

            'pending_bookings': {
                'today': today_pending_booking,
                'this_month': this_pending_month_booking,
                'last_month': last_pending_month_booking,
            },
            'completed_bookings': {
                'today': today_completed_booking,
                'this_month': this_completed_month_booking,
                'last_month': last_completed_month_booking,
            },
            'deleyed_bookings': {
                'today': today_delayed_booking,
                'this_month': this_delayed_month_booking,
                'last_month': last_delayed_month_booking,
            },
        }

class pr_testing_reminder(models.Model):
    _name = 'pt.reminder'

    reminder_count = fields.Integer('Reminder No')
    reminder_time = fields.Datetime('Reminder Date & Time')
    pr_book_id = fields.Many2one('project.booking')
    partner_ids = fields.Many2many('res.partner', string="Stackholders")

# class pr_testing_reminder(models.Model):
#     _name = 'project.booking.dashboard'
#
#     name = fields.Char('Name')
