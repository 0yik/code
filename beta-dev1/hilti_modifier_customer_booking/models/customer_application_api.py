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
# from ldif import start_time


class project_project(models.Model):
    _inherit = "project.project"
    
    @api.model
    def create_project_from_mobile(self, name):
        user_id = self.env['res.users'].search([('id', '=', self.env.uid)])
        project_search = self.sudo().search([('partner_id','=',user_id.partner_id.id),('is_new_project','=', True)])
        for a in project_search:
            a.unlink()
        project = self.with_context(created_from_user = 1).sudo().create({'name':name, 'partner_id':user_id.partner_id.id, 'is_new_project': True})
        return project and project.id
        
    
class timeslot_booking(models.Model):
    _inherit = 'timeslot.booking'
    
    
    @api.model
    def get_reschedule_tieslot_app(self, booking_date, project_booking_id):
        ctx = {}
        ctx.update({'calling_from_app': 1})
        if self.env.user:
            user_id = self.env['res.users'].search([('id', '=', self.env.uid)])
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        get_re_slot = self.with_context(ctx).sudo().get_reschedule_booking_slot(booking_date, project_booking_id)
        return get_re_slot
    
    @api.model
    def update_reschedule_timeslot_app(self, project_booking_id, time_slot_booking_ids, booking_date, booking_time):
        old_booking_rec = self.search([('pr_booking_id', '=', project_booking_id)])
        project_booking_id = self.env['project.booking'].browse([project_booking_id])
        if old_booking_rec:
            for an in old_booking_rec:
                an.unlink()
        if type(time_slot_booking_ids) == list:
            for aa in time_slot_booking_ids:
                new_id = self.browse([aa])
                new_id.pr_booking_id = project_booking_id and project_booking_id.id
                new_id.temp = False
                project_booking_id.user_tester_id = new_id.tester_id
        else:
            new_id = self.browse([time_slot_booking_ids])
            new_id.pr_booking_id = project_booking_id and project_booking_id.id
            new_id.temp = False
            project_booking_id.user_tester_id = new_id.tester_id
        return {'booking_done': True, 'booking_id': project_booking_id.booking_no,
                                    'booking_date': booking_date, 'booking_time': booking_time}
            
    @api.model
    def get_timeslot_for_mobile(self, booking_date, total_hours, all_anchors, project_id, sic, postal_code):
        ctx = {}
        tester_name = False
        tester_contact = False
        if all_anchors and all_anchors[0] == 'sic_booking':
            total_hours = [total_hours]
            sic = False
        if self.env.user:
            user_id = self.env['res.users'].search([('id', '=', self.env.uid)])
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        slot_time = False
        time_slot = self.env['timeslot.master'].sudo().search([], limit=1)
        final_time_id = []
        time_slot_based = False
        return_list = []
        if not time_slot.time_slot_based:
            time_slot_based = 'static'
            booking_logic = self.env['project.booking'].with_context(ctx).sudo().booking_logic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, slot_time)
            def call_booking_order_static(booking_logic):
                booking_logic = self.env['project.booking'].with_context(ctx).sudo().booking_logic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = self.env['project.booking'].with_context(ctx).sudo().booking_logic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
#                         booking_logic = call_booking_order(booking_logic)
                return booking_logic
            if type(booking_logic) == list:
                if booking_logic and booking_logic[0] != False:
                    booking_logic = call_booking_order_static(booking_logic)
            remaining_slot = []
            if type(booking_logic) != list and type(booking_logic) == dict:
                for slot_book in booking_logic.keys():
                    if slot_book:
                        tester_id = self.env['res.partner'].sudo().search([('id', '=', slot_book)])
                        if tester_id:
                            tester_name = tester_id.name
                            tester_contact = tester_id.phone
                    if type(booking_logic[slot_book]) != list:
                        slot_book_value = [booking_logic[slot_book]]
                    else:
                        slot_book_value = booking_logic[slot_book]
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
                                              'tester_name': tester_name,
                                              'tester_contact': tester_contact,
                                              'end':time.timeslot_end_id.end_time,
                                              'end_time':  end_time, })
            return_list.append(final_time_id)
            return_list.append(booking_date)
            return_list.append(time_slot_based)
            return return_list
        else:
            time_slot_based = 'dynamic'
            remaining_slot = []
            booking_logic = self.env['project.booking'].with_context(ctx).sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, slot_time)
            def call_booking_order(booking_logic):
                booking_logic = self.env['project.booking'].with_context(ctx).sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = self.env['project.booking'].with_context(ctx).sudo().booking_logic_dynamic(booking_date,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
#                         booking_logic = call_booking_order(booking_logic)
                return booking_logic
            if type(booking_logic) == list:
                if booking_logic and booking_logic[0] != False:
                    booking_logic = call_booking_order(booking_logic)
            if type(booking_logic) != list and type(booking_logic) == dict:
                for slot_book in booking_logic.keys():
                    slot_book_value = []
                    if slot_book:
                        tester_id = self.env['res.partner'].sudo().search([('id', '=', slot_book)])
                        if tester_id:
                            tester_name = tester_id.name
                            tester_contact = tester_id.phone
                    for aa in booking_logic[slot_book]:
                        if type(aa) != list:
                            slot_book_value.append(booking_logic[slot_book])
                            break
                        else:
                            slot_book_value = booking_logic[slot_book]
                            break
                    for time1 in slot_book_value:
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
                                              'tester_name': tester_name,
                                              'tester_contact': tester_contact,
                                              'end':time.timeslot_end_id.end_time,
                                              'end_time':  end_time, })
            return_list.append(final_time_id)
            return_list.append(booking_date)
            return_list.append(time_slot_based)
            return return_list
            

class project_booking(models.Model):
    _inherit = 'project.booking'
    
    
    @api.model
    def reschedule_sic_special_booking_from_app(self, start_date, start_time, end_date, end_time, booking_id):
        ctx = {}
        from datetime import datetime
        user_id = self.env['res.users'].search([('id', '=', self.env.uid)])
        ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        if start_time > 24.0 or end_time > 24.0:
            raise Warning(_("Please select proper time."))
        booking_id = self.env['project.booking'].sudo().browse([booking_id])
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
            booking_logic = self.env['project.booking'].sudo().with_context(ctx).dedicated_booking_logic(start_date,start_time,end_date,end_time,total_hours, all_anchors, booking_id.project_id.id, sic, booking_id.postal_code.name)
            if booking_logic == False:
                raise Warning(_("Testers are not available for the booking on (selected date time).Please select another date and time for your booking. Sorry for the inconvenience. Thank You."))
            else:
                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
                l_start_time = "%02d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)
                l_end_time = "%02d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)
                booking_start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                booking_end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()
                dt_start = datetime.combine(booking_start_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
                dt_end = datetime.combine(booking_end_date, datetime.strptime(l_end_time, "%H:%M:%S").time())
                from pytz import timezone
                local = timezone(user_id.tz)
                import pytz
                check_dt_start = datetime.strptime(str(dt_start), "%Y-%m-%d %H:%M:%S") 
                check_dt_end = datetime.strptime(str(dt_end), "%Y-%m-%d %H:%M:%S")
                dt_start = local.localize(check_dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_end = local.localize(check_dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                booking_id.with_context(ctx).write({'start_date_time': dt_start,'end_date_time': dt_end,
                                  'user_tester_id': tester_id and tester_id.id,
                                  'status': 'rescheduled'})
        if booking_id and booking_id.booking_type == 'sic':
            # 2017-12-08 13.00 15.50 398670
            booking_logic = self.env['project.booking'].sudo().with_context(ctx).sic_booking_logic(start_date,start_time,end_time,booking_id.postal_code.name)
            if booking_logic == False:
                raise Warning(_("Testers are not available for the booking on (selected date time).Please select another date and time for your booking. Sorry for the inconvenience. Thank You."))
            else:
                tester_id = self.env['res.users'].sudo().search([('partner_id', '=', int(booking_logic))])
                booking_id.tester_id.project_ids = [(3, booking_id.project_id.id)]
                tester_id.partner_id.project_ids = [(4, booking_id.project_id.id)]
                l_start_time = "%02d:%02d:%02d" % (int(start_time), (start_time*60) % 60, (start_time*3600) % 60)
                l_end_time = "%02d:%02d:%02d" % (int(end_time), (end_time*60) % 60, (end_time*3600) % 60)
                booking_start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                dt_start = datetime.combine(booking_start_date, datetime.strptime(l_start_time, "%H:%M:%S").time())
                dt_end = datetime.combine(booking_start_date, datetime.strptime(l_end_time, "%H:%M:%S").time())
                from pytz import timezone
                local = timezone(user_id.tz)
                import pytz
                from datetime import datetime
                check_dt_start = datetime.strptime(str(dt_start), "%Y-%m-%d %H:%M:%S") 
                check_dt_end = datetime.strptime(str(dt_end), "%Y-%m-%d %H:%M:%S")
                dt_start = local.localize(check_dt_start, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                dt_end = local.localize(check_dt_end, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                booking_id.with_context(ctx).write({'start_date_time': dt_start,'end_date_time': dt_end,
                                  'user_tester_id': tester_id and tester_id.id,
                                  'status': 'rescheduled'})
        return True
        
    
    
    @api.model
    def get_project_and_address_app(self):
        all_projects = []
        project_id = self.env['project.project'].sudo().search([('status','=', 'approved')], order="id desc")
        user_id = self.env['res.users'].search([('id', '=', self.env.uid)])
        if user_id and user_id.partner_id and user_id.partner_id.id:
            new_project_id = self.env['project.project'].sudo().search([('is_new_project','=', True),('partner_id','=', user_id.partner_id.id),('status','!=', 'approved')], order="id desc", limit=1)
            if new_project_id:
                all_projects.append([new_project_id.id, new_project_id.name, '', '', 'new'])
        for a in project_id:
            address = ''
            postal_code = ''
            if a.location_id and a.location_id.address:
                address = a.location_id.address
            if a.postal_code and a.postal_code.name:
                postal_code = a.postal_code.name
            all_projects.append([a.id, a.name, address, postal_code, 'exist'])
        return all_projects
    
    
    
    @api.model
    def check_project_is_new_app(self, project_id):
        if project_id:
            new_pr_id = self.env['project.project'].sudo().search([('id', '=', project_id),('is_new_project', '=', True)])
            if new_pr_id:
                return True
            else:
                return False
        

    @api.model
    def create_timeslot_application(self, date, tester_id, time_slot_id):
        booking_record = []
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        tester_id = self.env['res.users'].sudo().search([('partner_id', '=', tester_id)])
        if date and time_slot_id:
            time_slot_booking_record = self.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
            if time_slot_booking_record:
                for tm in time_slot_booking_record:
                    tm.unlink()
            if type(time_slot_id) == list:
                all_book = []
                for exist_id in list(time_slot_id):
                    time_slot_booking = self.env['timeslot.booking'].sudo().create({'time_slot_id': exist_id, 'tester_id': tester_id and tester_id.id,'user_id': user_id and user_id.id, 'booking_date': date, 'temp': True})
                    all_book.append(time_slot_booking)
                time_slot_booking = all_book
            else:
                time_slot_booking = self.env['timeslot.booking'].sudo().create({'time_slot_id': time_slot_id, 'tester_id': tester_id and tester_id.id,'user_id': user_id and user_id.id, 'booking_date': date, 'temp': True})
            if time_slot_booking and time_slot_booking[0]:
                start = int(time_slot_booking[0].timeslot_start_id.start_time)
                if len(time_slot_booking) >= 2:
                    end = int(time_slot_booking[1].timeslot_end_id.end_time)
                    send_end_time = time_slot_booking[1].timeslot_end_id.end_time
                    end_time = "%02d:%02d" % (int(time_slot_booking[1].timeslot_end_id.end_time), (time_slot_booking[1].timeslot_end_id.end_time * 60) % 60)
                else:
                    send_end_time = time_slot_booking[0].timeslot_end_id.end_time
                    end = int(time_slot_booking[0].timeslot_end_id.end_time)
                    end_time = "%02d:%02d" % (int(time_slot_booking[0].timeslot_end_id.end_time), (time_slot_booking[0].timeslot_end_id.end_time * 60) % 60)
                for aa in time_slot_booking:
                    send_end_time = aa.timeslot_end_id.end_time
                    end = int(aa.timeslot_end_id.end_time)
                    end_time = "%02d:%02d" % (int(aa.timeslot_end_id.end_time), (aa.timeslot_end_id.end_time * 60) % 60)
                start_time = "%02d:%02d" % (int(time_slot_booking[0].timeslot_start_id.start_time), (time_slot_booking[0].timeslot_start_id.start_time * 60) % 60)
                if start > 12:
                    start = (start - 12)
                    start_time = "%02d:%02d" % ((int(time_slot_booking[0].timeslot_start_id.start_time) - 12), (time_slot_booking[0].timeslot_start_id.start_time * 60) % 60)
                if end > 12:
                    end = (end - 12)
                    end_time = "%d:%02d" % ((int(time_slot_booking[0].timeslot_end_id.end_time) - 12), (time_slot_booking[0].timeslot_end_id.end_time * 60) % 60)
                booking_record.append({'start':time_slot_booking[0].timeslot_start_id.start_time,
                                          'start_time':  start_time,
                                          'Booking_date': time_slot_booking[0].booking_date,
                                          'end':send_end_time,
                                          'end_time':  end_time, 'time_slot_booking_ids': [aa.id for aa in time_slot_booking]})
            else:
                booking_record.append({'start': False,
                                          'start_time':  False,
                                          'Booking_date': False,
                                          'end':False,
                                          'end_time':  False,
                                          'time_slot_booking_ids': False})
        return booking_record
    
    @api.model
    def create_project_booking_from_application(self, b_time, pr_postal_code, tm_id, pr_address, co_name, co_no, all_anchor, sic, b_date, booking_type, project_id):
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        ctx = {}
        ctx.update({'create_from_website': True})
        if user_id:
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        # Anchor is remaining.
        create_dict = {}
        return_done = {}
        booking_id = False
        postal_code_id = False
        anchor_create_list = []
        if all_anchor:
            for an in all_anchor:
                anchor_create_list.append((0,0,{'name': an[0], 'anchor_type_id': an[1], 'anchor_size_id': an[2], 'anchor_qty': an[3],'an_complexity': an[4]}))
        if pr_postal_code:
            postal_code_id = self.env['postal.code'].sudo().search([('name', '=', pr_postal_code)])
            if not postal_code_id:
                postal_code_id = self.env['postal.code'].sudo().create({'name': pr_postal_code})
            if postal_code_id:
                postal_code_id = postal_code_id.id
        location_id = self.env['location.location'].sudo().create({'postal_code': postal_code_id,
                                                                'address': pr_address,
                                                                'project_id': project_id})
        if location_id:
            location_id = location_id.id
        if sic == True:
            sic = True
        else:
            sic = False
        if booking_type == 'normal':
            create_dict.update({'project_id': project_id, 'contact_id': co_name,
                                'contact_number': co_no, 'sid_required': sic,
                                'partner_id': user_id.partner_id and user_id.partner_id.id,
                                'booking_type': booking_type, 'location_id': location_id,
                                'is_final': True, 'user_id': user_id and user_id.id or False,
                                'project_booking_anchor_ids': anchor_create_list,
                                'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id or False})
            booking_id = self.env['project.booking'].with_context(ctx).create(create_dict)
            if type(tm_id) == tuple:
                time_slot_booking_id_all = self.env['timeslot.booking'].sudo().search([('id', 'in', tm_id)])
                for time_slot_booking_id in time_slot_booking_id_all:
                    time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                    booking_id.with_context(ctx).write({'user_tester_id': time_slot_booking_id.tester_id and time_slot_booking_id.tester_id.id})
                    time_slot_booking_id.temp = False
            else:
                time_slot_booking_id = self.env['timeslot.booking'].sudo().search([('id', '=', tm_id)])
                if time_slot_booking_id:
                    time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                    booking_id.with_context(ctx).write({'user_tester_id': time_slot_booking_id.tester_id and time_slot_booking_id.tester_id.id})
                    time_slot_booking_id.temp = False
            time_slot_booking = self.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
            if time_slot_booking:
                for tm in time_slot_booking:
                    tm.unlink()
            return_done.update({'booking_done': True, 'booking_id': booking_id.booking_no,
                                    'booking_date': b_date, 'booking_time': b_time})
            if project_id:
                ch_pr_id = self.env['project.project'].sudo().search([('id', '=', project_id)])
                if ch_pr_id and not ch_pr_id.location_id:
                    ch_pr_id.location_id = location_id
                if ch_pr_id:
                    ch_pr_id.is_new_project = False
        return return_done
    
    @api.model
    def create_project_booking_from_application_sic(self, b_time, pr_postal_code, tm_id, pr_address, co_name, co_no, sic, b_date, project_id, sic_booking_time):
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        ctx = {}
        ctx.update({'create_from_website': True})
        if user_id:
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        # Anchor is remaining.
        create_dict = {}
        return_done = {}
        booking_id = False
        postal_code_id = False
        if pr_postal_code:
            postal_code_id = self.env['postal.code'].sudo().search([('name', '=', pr_postal_code)])
            if not postal_code_id:
                postal_code_id = self.env['postal.code'].sudo().create({'name': pr_postal_code})
            if postal_code_id:
                postal_code_id = postal_code_id.id
        location_id = self.env['location.location'].sudo().create({'postal_code': postal_code_id,
                                                                'address': pr_address,
                                                                'project_id': project_id})
        if location_id:
            location_id = location_id.id
        sic = True
        create_dict.update({'project_id': project_id, 'contact_id': co_name,
                            'contact_number': co_no, 'sid_required': sic,
                            'partner_id': user_id.partner_id and user_id.partner_id.id,
                            'booking_type': 'sic', 'location_id': location_id,
                            'is_final': True, 'user_id': user_id and user_id.id or False,
                            'sic_required_hours': sic_booking_time,
                            'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id or False})
        booking_id = self.env['project.booking'].with_context(ctx).create(create_dict)
        sic_tester_id = False
        if type(tm_id) == tuple:
            time_slot_booking_id_all = self.env['timeslot.booking'].sudo().search([('id', 'in', tm_id)])
            for time_slot_booking_id in time_slot_booking_id_all:
                time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                booking_id.with_context(ctx).write({'user_tester_id': time_slot_booking_id.tester_id and time_slot_booking_id.tester_id.id})
                time_slot_booking_id.temp = False
                sic_tester_id = time_slot_booking_id.tester_id
        else:
            time_slot_booking_id = self.env['timeslot.booking'].sudo().search([('id', '=', tm_id)])
            if time_slot_booking_id:
                time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                booking_id.with_context(ctx).write({'user_tester_id': time_slot_booking_id.tester_id and time_slot_booking_id.tester_id.id})
                time_slot_booking_id.temp = False
                sic_tester_id = time_slot_booking_id.tester_id
        time_slot_booking = self.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
        if sic_tester_id:
            sic_tester_id.partner_id.project_ids = [(4, int(project_id))]
        if time_slot_booking:
            for tm in time_slot_booking:
                tm.unlink()
        return_done.update({'booking_done': True, 'booking_id': booking_id.booking_no,
                                'booking_date': b_date, 'booking_time': b_time})
        if project_id:
            ch_pr_id = self.env['project.project'].sudo().search([('id', '=', project_id)])
            if ch_pr_id and not ch_pr_id.location_id:
                ch_pr_id.location_id = location_id
            if ch_pr_id:
                ch_pr_id.is_new_project = False
        return return_done
            
    @api.model
    def get_anchor_size_from_application(self, size_id):
        anchor_size = []
        anchor_master = self.env['anchor.master'].sudo().search([('anchor_type_id', '=', int(size_id))])
        hours1 = []
        hours2 = []
        hours3 = []
        image1 = []
        image2 = []
        image3 = []
        if anchor_master:
            hours1.append(anchor_master.simple_time)
            hours2.append(anchor_master.medium_time)
            hours3.append(anchor_master.complex_time)
            image1.append(anchor_master.simple_image)
            image2.append(anchor_master.medium_image)
            image3.append(anchor_master.complex_image)
            for size in anchor_master.anchor_size_id:
                anchor_size.append({'id': size.id, 'name': size.name})
        return [anchor_size, hours1, hours2, hours3, image1, image2, image3]
    
    @api.model
    def dedicated_support_tester_app(self, start_date,start_time,end_date,end_time,total_hours, all_anchors, project_id, sic, postal_code):
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        ctx = {}
        tester_name = False
        tester_contact = False
        if user_id:
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        if all_anchors and all_anchors[0] and all_anchors[0] == 'sic_booking':
            sic = 'no'
            total_hours = []
        booking_logic = self.env['project.booking'].with_context(ctx).sudo().dedicated_booking_logic(start_date,start_time,end_date,end_time,total_hours, all_anchors, project_id, sic, postal_code)
        if booking_logic:
            tester_id = self.env['res.partner'].sudo().search([('id', '=', booking_logic)])
            if tester_id:
                tester_name = tester_id.name
                tester_contact = tester_id.phone
        return {'tester_id': booking_logic, 'tester_name': tester_name, 'tester_contact': tester_contact}
    
    @api.model
    def create_dedicate_supp_booking_from_application(self, booking_start,booking_end, pr_postal_code, tester_id, pr_address, co_name, co_no, all_anchor, sic, project_id):
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        ctx = {}
        ctx.update({'create_from_website': True})
        if user_id:
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        # Anchor is remaining.
        create_dict = {}
        return_done = {}
        booking_id = False
        postal_code_id = False
        anchor_create_list = []
        if all_anchor and all_anchor[0] and all_anchor[0] != 'sic_booking':
            if all_anchor:
                for an in all_anchor:
                    anchor_create_list.append((0,0,{'name': an[0], 'anchor_type_id': an[1], 'anchor_size_id': an[2], 'anchor_qty': an[3],'an_complexity': an[4]}))
        if pr_postal_code:
            postal_code_id = self.env['postal.code'].sudo().search([('name', '=', pr_postal_code)])
            if not postal_code_id:
                postal_code_id = self.env['postal.code'].sudo().create({'name': pr_postal_code})
            if postal_code_id:
                postal_code_id = postal_code_id.id
        location_id = self.env['location.location'].sudo().create({'postal_code': postal_code_id,
                                                                'address': pr_address,
                                                                'project_id': project_id})
        if location_id:
            location_id = location_id.id
        if tester_id == 0:
            tester_id = False
        tester_id = self.env['res.users'].sudo().search([('partner_id', '=', tester_id)])
        if tester_id:
            if all_anchor and all_anchor[0] and all_anchor[0] != 'sic_booking':
                tester_id.partner_id.project_ids = [(4, int(project_id))]
            tester_id = tester_id.id
        if sic == True:
            sic = True
        else:
            sic = False
        if tester_id == False:
            ctx.update({'send_notification_to_testers': True})
            create_dict.update({'project_id': project_id, 'contact_id': co_name,
                                    'contact_number': co_no, 'sid_required': sic,
                                    'partner_id': user_id.partner_id and user_id.partner_id.id,
                                    'booking_type': 'special', 'location_id': location_id,
                                    'is_final': False, 'user_id': user_id and user_id.id or False,
                                    'project_booking_anchor_ids': anchor_create_list,
                                    'user_tester_id': tester_id,
                                    'start_date_time': booking_start,
                                    'end_date_time': booking_end,
                                    'add_accept_button': True,
                                    'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id or False})
        else:
            create_dict.update({'project_id': project_id, 'contact_id': co_name,
                                    'contact_number': co_no, 'sid_required': sic,
                                    'partner_id': user_id.partner_id and user_id.partner_id.id,
                                    'booking_type': 'special', 'location_id': location_id,
                                    'is_final': True, 'user_id': user_id and user_id.id or False,
                                    'project_booking_anchor_ids': anchor_create_list,
                                    'user_tester_id': tester_id,
                                    'start_date_time': booking_start,
                                    'end_date_time': booking_end,
                                    'add_accept_button': False,
                                    'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id or False})
        booking_id = self.env['project.booking'].with_context(ctx).create(create_dict)
        from pytz import timezone
        local = timezone(user_id.tz)
        import pytz
        from datetime import datetime
        start_datetime = datetime.strptime(booking_id.start_date_time, "%Y-%m-%d %H:%M:%S")
        start_date = local.localize(start_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_datetime = datetime.strptime(booking_id.end_date_time, "%Y-%m-%d %H:%M:%S")
        end_date = local.localize(end_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        booking_id.with_context(ctx).write({'start_date_time': start_date, 'end_date_time': end_date,
                          'final_start_dtime': start_date, 'final_end_dtime': end_date})
        if project_id:
            ch_pr_id = self.env['project.project'].sudo().search([('id', '=', project_id)])
            if ch_pr_id and not ch_pr_id.location_id:
                ch_pr_id.location_id = location_id
            if ch_pr_id:
                ch_pr_id.is_new_project = False
        return {'booking_special_done': True, 'booking_id': booking_id.booking_no, 'booking_start_date': booking_start, 'booking_end_date': booking_end}
    
    
    @api.model
    def sic_request_tester_app(self, booking_date, start_time, end_time, postal_code):
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        ctx = {}
        if user_id:
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        booking_logic = self.env['project.booking'].with_context(ctx).sudo().sic_booking_logic(booking_date, start_time, end_time, postal_code)
        if booking_logic in ['None', 'none', ''] or not booking_logic:
            return False
        else:
            return booking_logic
    
    
    @api.model
    def create_sic_booking_from_application(self, booking_start,booking_end, pr_postal_code, tester_id, pr_address, co_name, co_no, project_id):
        user_id = self.env['res.users'].sudo().browse(self.env.uid)
        ctx = {}
        ctx.update({'create_from_website': True})
        if user_id:
            ctx.update({'tz': user_id.tz, 'uid': self.env.uid})
        # Anchor is remaining.
        create_dict = {}
        return_done = {}
        booking_id = False
        postal_code_id = False
        if pr_postal_code:
            postal_code_id = self.env['postal.code'].sudo().search([('name', '=', pr_postal_code)])
            if not postal_code_id:
                postal_code_id = self.env['postal.code'].sudo().create({'name': pr_postal_code})
            if postal_code_id:
                postal_code_id = postal_code_id.id
        location_id = self.env['location.location'].sudo().create({'postal_code': postal_code_id,
                                                                'address': pr_address,
                                                                'project_id': project_id})
        if location_id:
            location_id = location_id.id
        tester_id = self.env['res.users'].sudo().search([('partner_id', '=', tester_id)])
        sic = True
        create_dict.update({'project_id': project_id, 'contact_id': co_name,
                                'contact_number': co_no, 'sid_required': sic,
                                'partner_id': user_id.partner_id and user_id.partner_id.id,
                                'booking_type': 'sic', 'location_id': location_id,
                                'is_final': True, 'user_id': user_id and user_id.id or False,
                                'user_tester_id': tester_id and tester_id.id,
                                'start_date_time': booking_start,
                                'end_date_time': booking_end,
                                'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id or False})
        booking_id = self.env['project.booking'].with_context(ctx).create(create_dict)
        from pytz import timezone
        local = timezone(user_id.tz)
        import pytz
        from datetime import datetime
        start_datetime = datetime.strptime(booking_id.start_date_time, "%Y-%m-%d %H:%M:%S")
        start_date = local.localize(start_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        end_datetime = datetime.strptime(booking_id.end_date_time, "%Y-%m-%d %H:%M:%S")
        end_date = local.localize(end_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        booking_id.with_context(ctx).write({'start_date_time': start_date, 'end_date_time': end_date,
                          'final_start_dtime': start_date, 'final_end_dtime': end_date})
        if project_id:
            ch_pr_id = self.env['project.project'].sudo().search([('id', '=', project_id)])
            if ch_pr_id and not ch_pr_id.location_id:
                ch_pr_id.location_id = location_id
            if ch_pr_id:
                ch_pr_id.is_new_project = False
        return {'booking_special_done': True, 'booking_id': booking_id.booking_no, 'booking_start_date': booking_start, 'booking_end_date': booking_end}
        