from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
import werkzeug
import json
import base64
import os
from random import randint
import logging
import datetime
import time
import pytz
from dateutil import tz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT

class HiltiBooking(http.Controller):

    @http.route(['/map_for_mobile'], type='http', auth="public", website=True)
    def map_for_mobile(self, **post):
        return http.request.render("hilti_modifier_customer_booking.map_for_mobile", {})

    @http.route(['/booking'], type='http', auth="user", website=True)
    def customer_booking(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        master_ids = request.env['anchor.type'].sudo().search([])
        #master_size_ids = request.env['anchor.size'].sudo().search([])
        group_hilti_account_manager = user_id.has_group('hilti_modifier_accessrights.group_hilti_account_manager')
        group_hilti_admin = user_id.has_group('hilti_modifier_accessrights.group_hilti_admin')
        group_hilti_engineers = user_id.has_group('hilti_modifier_accessrights.group_hilti_engineers')
        group_hilti_customer_service = user_id.has_group('hilti_modifier_accessrights.group_hilti_customer_service')
        group_hilti_customer = user_id.has_group('hilti_modifier_accessrights.group_hilti_customer')
        is_new_pr = 0
        is_display_parter = 0
        project_id_new = False
        project_id = request.env['project.project'].sudo().search(['|', ('status','=', 'approved'),('is_new_project','=', True)], order="id desc")
        if user_id and user_id.partner_id and user_id.partner_id.id:
            new_project_id = request.env['project.project'].sudo().search([('is_new_project','=', True),('partner_id','=', user_id.partner_id.id),('status','!=', 'approved')], order="id desc", limit=1)
            if new_project_id:
                is_new_pr = 1
                project_id_new = new_project_id.id
        customer = ''
        partner_id = request.env['res.partner'].sudo().search([('type_of_user', '=', 'hilti_customer')])
        
        if group_hilti_customer:
        	customer = user_id.partner_id
        if group_hilti_account_manager:
        	is_display_parter = 1
        if group_hilti_engineers:
        	is_display_parter = 1
        if group_hilti_admin:
        	is_display_parter = 1
        if group_hilti_customer_service:
        	is_display_parter = 1
        return http.request.render("hilti_modifier_customer_booking.customer_booking_template", {'project_id': project_id, 'partner_id': partner_id, 'is_new_pr': is_new_pr, 'project_id_new': project_id_new,'master_ids': master_ids, 'master_size_ids': [], 'is_display_parter': is_display_parter, 'customer': customer})


    @http.route(['/get_project_address'], type='json', auth="user", website=True)
    def get_project_address(self, **post):
        temp = []
        if post and post['project_id'] and not post['project_id'] == 'create':
            new_pr_id = request.env['project.project'].sudo().search([('id', '=', post['project_id'])])
            if new_pr_id.location_id:
                temp = [new_pr_id.location_id.address, new_pr_id.postal_code and new_pr_id.postal_code.name]
        return temp


    @http.route(['/check_project_is_new'], type='json', auth="user", website=True)
    def check_project_is_new(self, **post):
        temp = [0,0]
        if post and post['project_id']:
            new_pr_id = request.env['project.project'].sudo().search([('id', '=', post['project_id']),('is_new_project', '=', True)])
            if new_pr_id:
                temp[0] = 1
            if new_pr_id.status == 'draft':
                temp[1] = 1
        return temp


    @http.route(['/get_anchor_size'], type='json', auth="user", website=True)
    def get_anchor_size(self, **post):
        an_id = post['selected_id']
        anchor_master = request.env['anchor.master'].sudo().search([('anchor_type_id', '=', int(an_id))])
        anchor_size = []
        image1 = []
        image2 = []
        image3 = []
        hours1 = []
        hours2 = []
        hours3 = []
        if anchor_master:
            image1.append(anchor_master.simple_image)
            hours1.append(anchor_master.simple_time)
            image2.append(anchor_master.medium_image)
            hours2.append(anchor_master.medium_time)
            image3.append(anchor_master.complex_image)
            hours3.append(anchor_master.complex_time)
            for size in anchor_master.anchor_size_id:
                anchor_size.append({'id': size.id, 'name': size.name})
        return [anchor_size, image1, image2, image3, hours1, hours2, hours3]

    @http.route(['/my_booking'], type='http', auth="user", website=True)
    def my_booking(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'menu_my_booking')[1]
        action_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'action_my_booking_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))

    @http.route(['/my_booking_customer'], type='http', auth="user", website=True)
    def my_booking_customer(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'menu_my_booking')[1]
        action_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'action_my_booking_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))


    @http.route(['/my_dashboard'], type='http', auth="user", website=True)
    def my_dashboard(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_customer_booking', 'menu_project_booking_dahboard_tester')[1]
        action_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_customer_booking', 'project_booking_dashboard_act')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))
    
    @http.route(['/customer_bookings_admin'], type='http', auth="user", website=True)
    def customer_bookings_admin(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'menu_action_admin_booking_view')[1]
        action_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'action_admin_booking_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))
    
    
    @http.route(['/customer_bookings_staff'], type='http', auth="user", website=True)
    def customer_bookings_staff(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'menu_action_other_user_booking_view')[1]
        action_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_company', 'action_admin_booking_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))
    
    
    @http.route(['/my_dashboard_customer'], type='http', auth="user", website=True)
    def my_dashboard_customer(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_customer_booking', 'menu_project_booking_dahboard_customer')[1]
        action_id = request.env['ir.model.data'].get_object_reference(
            'hilti_modifier_customer_booking', 'project_booking_dashboard_act')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))

    @http.route(['/my_tasks'], type='http', auth="user", website=True)
    def my_tasks(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_company', 'menu_action_my_booking_view_tester')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_company', 'action_my_booking_view_tester')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))

    @http.route(['/masters'], type='json', auth="user", website=True)
    def masters(self, **post):
        final_project_id = []
        final_size_id = []
        user_id = request.env['res.users'].sudo().browse(request.uid)
        master_ids = request.env['anchor.type'].sudo().search([])
        master_size_ids = request.env['anchor.size'].sudo().search([])
        if master_size_ids:
            for size in master_size_ids:
                final_size_id.append({'id':size.id,
                                   'name':size.name})
        if master_ids:
            for master in master_ids:
                final_project_id.append({'id':master.id,
                                   'name':master.name})
        return [final_project_id, []]

    @http.route(['/holydays'], type='json', auth="user", website=True)
    def holidays(self, date, cellMonth, cellYear, **post):
        date1 = '%d-%02d-%02d' % (cellYear, cellMonth, date)
        holidays_ids = request.env['holiday.holiday'].sudo().search([('holiday_date', '=', date1)])
        time_slot = request.env['timeslot.master'].sudo().search([], limit=1)
        book_ids = request.env['timeslot.booking'].sudo().search([('booking_date', '=', date1)])
        count = 0
        book_count = 0
        for time in time_slot.time_slot_ids:
            count += 1
        for book in book_ids:
            book_count += 1
        return_list = []
        if holidays_ids:
            return_list.append(1)
        else:
            return_list.append(2)
        if count != 0 and book_count != 0 and count == book_count:
            return_list.append(10)
        else:
            return_list.append(20)
        return return_list

    @http.route(['/booking_all'], type='json', auth="user", website=True)
    def customer_booking_all(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        project_id = []
        final_project_id = []
        if user_id.partner_id and user_id.partner_id.project_ids:
            project_id = request.env['project.project'].sudo().search([('partner_id', '=', user_id.partner_id.id)], order="id desc")
            for project in project_id[5:]:
                final_project_id.append({'id':project.id,
                                   'name':project.name})
        return final_project_id

    @http.route(['/total_month_display'], type='json', auth="user", website=True)
    def total_month_display_calendar(self, **post):
        time_slot = request.env['timeslot.master'].sudo().search([], limit=1)
        if time_slot and time_slot.calandar_display:
            return time_slot.calandar_display
        else:
            return 0

    @http.route(['/create_anchor_project'], type='json', auth="user", website=True)
    def create_anchor_project(self, **post):
        if post and 'an_size' in post.keys() and 'an_type' in post.keys():
            pr_booking_an = request.env['project.booking.anchor'].sudo().create({'anchor_type_id': post.get('an_type'),
                                                                                 'anchor_size_id': post.get('an_size'),
                                                                                 'anchor_qty': post.get('an_qty'),
                                                                                 'an_complexity': post.get('redio_val'),
                                                                                 'name': post.get('an_name')})
        return pr_booking_an.id


    @http.route(['/create_time_slot'], type='json', auth="user", website=True)
    def create_time_slot(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        tester_id = request.env['res.users'].sudo().search([('partner_id', '=', int(post.get('tester_id')))])
        if post and 'date' in post.keys() and 'time_slot_id' in post.keys():
            time_slot_booking_record = request.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
            if time_slot_booking_record:
                for tm in time_slot_booking_record:
                    tm.unlink()
            if type(eval(post.get('time_slot_id'))) == tuple:
                for exist_id in list(eval(post.get('time_slot_id'))):
                    time_slot_booking = request.env['timeslot.booking'].sudo().create({'time_slot_id': exist_id, 'tester_id': tester_id and tester_id.id,'user_id': user_id and user_id.id, 'booking_date': post.get('date'), 'temp': True})
            else:
                time_slot_booking = request.env['timeslot.booking'].sudo().create({'time_slot_id': post.get('time_slot_id'), 'tester_id': tester_id and tester_id.id,'user_id': user_id and user_id.id, 'booking_date': post.get('date'), 'temp': True})
        return True


    @http.route(['/user_book_slot'], type='json', auth="user", website=True)
    def user_book_slot(self, **post):
        booking_record = []
        user_id = request.env['res.users'].sudo().browse(request.uid)
        time_slot_booking = request.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)])
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
            tester_name = ''
            tester_phone = ''
            if time_slot_booking[0].tester_id and time_slot_booking[0].tester_id.partner_id:
                tester_name = time_slot_booking[0].tester_id.partner_id.name
                tester_phone = time_slot_booking[0].tester_id.partner_id.phone
            start_time = "%02d:%02d" % (int(time_slot_booking[0].timeslot_start_id.start_time), (time_slot_booking[0].timeslot_start_id.start_time * 60) % 60)
            if start > 12:
                start = (start - 12)
                start_time = "%02d:%02d" % ((int(time_slot_booking[0].timeslot_start_id.start_time) - 12), (time_slot_booking[0].timeslot_start_id.start_time * 60) % 60)
            if end > 12:
                end = (end - 12)
                end_time = "%d:%02d" % ((int(send_end_time) - 12), (send_end_time * 60) % 60)
            booking_record.append({'start':time_slot_booking[0].timeslot_start_id.start_time,
                                      'start_time':  start_time,
                                      'tester_name':tester_name,
                                      'tester_contact': tester_phone,
                                      'Booking_date': datetime.datetime.strptime(time_slot_booking[0].booking_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
                                      'end':send_end_time,
                                      'end_time':  end_time, 'time_slot_booking': [aa.id for aa in time_slot_booking]})
        else:
            booking_record.append({'start': False,
                                      'start_time':  False,
                                      'Booking_date': False,
                                      'end':False,
                                      'tester_name':'',
                                      'tester_contact': '',
                                      'end_time':  False,
                                      'time_slot_booking': False})
        return booking_record

    @http.route(['/dedicated_support_tester'], type='json', auth="user", website=True)
    def dedicated_support_tester(self, start_time, start_date,end_time, end_date, total_hours, all_anchors, project_id, sic, postal_code, **post):
        start_time = "%02d.%02d" % (int(start_time.split(':')[0]), ((int(start_time.split(':')[1]) * 100) / 60))
        end_time = "%02d.%02d" % (int(end_time.split(':')[0]), ((int(end_time.split(':')[1]) * 100) / 60))
        from datetime import datetime
        cus_date = datetime.strptime(start_date, "%d-%m-%Y").date()
        start_date = cus_date.strftime("%Y-%m-%d")
        cus_date_end = datetime.strptime(end_date, "%d-%m-%Y").date()
        end_date = cus_date_end.strftime("%Y-%m-%d")
        if all_anchors and all_anchors[0] and all_anchors[0] == 'sic_booking':
            sic = 'no'
            total_hours = []
        booking_logic = request.env['project.booking'].sudo().dedicated_booking_logic(start_date,start_time,end_date,end_time,total_hours, all_anchors, project_id, sic, postal_code)
        return_list = []
        return_list.append(booking_logic)
        user_login_id = request.env['res.users'].sudo().browse(request.uid)
        customer_booking_days = request.env['ir.values'].get_default('admin.configuration', 'customer_booking_days')
        group_hilti_admin = user_login_id.has_group('hilti_modifier_accessrights.group_hilti_admin')
        group_hilti_customer = user_login_id.has_group('hilti_modifier_accessrights.group_hilti_customer')
        import datetime
        now = datetime.datetime.now().strftime ("%Y-%m-%d")
        from datetime import datetime
        d1 = datetime.strptime(str(now), "%Y-%m-%d")
        d2 = datetime.strptime(str(start_date), "%Y-%m-%d")
        if customer_booking_days and customer_booking_days > 0 and group_hilti_customer == False and group_hilti_admin == False:
            if int(customer_booking_days) > abs((d2 - d1).days):
                return ['penalty']
        if booking_logic:
            ts_id = request.env['res.partner'].sudo().browse([booking_logic])
            return_list.append(ts_id.name)
            return_list.append(ts_id.phone)
        else:
            return_list.append(False)
            return_list.append(False)
        return return_list


#     @http.route(['/sic_request_tester'], type='json', auth="user", website=True)
#     def sic_request_tester(self, booking_date, start_time, end_time, postal_code, **post):
#         start_time = "%02d.%02d" % (int(start_time.split(':')[0]), ((int(start_time.split(':')[1]) * 100) / 60))
#         end_time = "%02d.%02d" % (int(end_time.split(':')[0]), ((int(end_time.split(':')[1]) * 100) / 60))
#         from datetime import datetime
#         cus_date = datetime.strptime(booking_date, "%d-%m-%Y").date()
#         final_booking_date = cus_date.strftime("%Y-%m-%d")
#         booking_logic = request.env['project.booking'].sudo().sic_booking_logic(final_booking_date, start_time, end_time, postal_code)
#         return_list = []
#         return_list.append(booking_logic)
#         user_login_id = request.env['res.users'].sudo().browse(request.uid)
#         customer_booking_days = request.env['ir.values'].get_default('admin.configuration', 'customer_booking_days')
#         group_hilti_admin = user_login_id.has_group('hilti_modifier_accessrights.group_hilti_admin')
#         group_hilti_customer = user_login_id.has_group('hilti_modifier_accessrights.group_hilti_customer')
#         import datetime
#         now = datetime.datetime.now().strftime ("%Y-%m-%d")
#         from datetime import datetime
#         d1 = datetime.strptime(str(now), "%Y-%m-%d")
#         d2 = datetime.strptime(str(final_booking_date), "%Y-%m-%d")
#         if customer_booking_days and customer_booking_days > 0 and group_hilti_customer == False and group_hilti_admin == False:
#             if int(customer_booking_days) > abs((d2 - d1).days):
#                 return ['penalty']
#         if booking_logic:
#             ts_id = request.env['res.partner'].sudo().browse([booking_logic])
#             return_list.append(ts_id.name)
#             return_list.append(ts_id.phone)
#         else:
#             return_list.append(False)
#             return_list.append(False)
#         return return_list

    @http.route(['/all_slot'], type='json', auth="user", website=True)
    def all_slot(self, date, cellMonth, cellYear, total_hours, all_anchors, project_id, sic, postal_code, **post):
        if all_anchors and all_anchors[0] == 'sic_booking':
            total_hours = "%02d.%02d" % (int(total_hours.split(':')[0]), ((int(total_hours.split(':')[1]) * 100) / 60))
            total_hours = [total_hours]
        user_login_id = request.env['res.users'].sudo().browse(request.uid)
        customer_booking_days = request.env['ir.values'].get_default('admin.configuration', 'customer_booking_days')
        group_hilti_admin = user_login_id.has_group('hilti_modifier_accessrights.group_hilti_admin')
        group_hilti_customer = user_login_id.has_group('hilti_modifier_accessrights.group_hilti_customer')
        date1 = '%d-%02d-%02d' % (cellYear, cellMonth, date)
        import datetime
        now = datetime.datetime.now().strftime ("%Y-%m-%d")
        from datetime import datetime
        d1 = datetime.strptime(str(now), "%Y-%m-%d")
        d2 = datetime.strptime(str(date1), "%Y-%m-%d")
        if customer_booking_days and customer_booking_days > 0 and group_hilti_customer == False and group_hilti_admin == False:
            if int(customer_booking_days) > abs((d2 - d1).days):
                return ['penalty',("Staff are not allowed to book %s days in advance for this Customer due to the restriction of Penalty days for Non-VIP Customers. Please inform the Customer / contact your admin for further assistance.") % customer_booking_days]
       # print "------------ss------", date1, total_hours, all_anchors, project_id, sic, postal_code
        #2017-12-21 [u'2'] [[u'2', u'1']] 9 no 398670
        slot_time = False
        time_slot = request.env['timeslot.master'].sudo().search([], limit=1)
        if time_slot.time_slot_based:
            time_slot_based = 1
        else:
            time_slot_based = 0
        # time_slot_based == is dynamic and  == static
        if time_slot_based == 0:
            all_time_diff = request.env['time.slot.start.end'].sudo().search([])
            slot_time_check = sum([float(eval(a)) for a in total_hours])
            duration_bigger = [a.id for a in all_time_diff if (a.timeslot_end_id.end_time - a.timeslot_start_id.start_time) >= slot_time_check]
            if not duration_bigger and all_anchors and all_anchors[0] != 'sic_booking':
                return ['penalty',("The time required for anchor testing is approximately %s hours according to the anchor selection. Timeslots for this duration is not available.Kindly use the Dedicated Support link below the BOOK button to make your booking. Thank You.") % slot_time_check]
            if not duration_bigger and all_anchors and all_anchors[0] == 'sic_booking':
                return ['penalty',("The time required for sic is approximately %s hours. Timeslots for this duration is not available.Kindly use the Dedicated Support link below the BOOK button to make your booking. Thank You.") % slot_time_check]
            booking_logic = request.env['project.booking'].sudo().booking_logic(date1,total_hours, all_anchors, project_id, sic, postal_code, slot_time)
            def call_booking_order_static(booking_logic):
                booking_logic = request.env['project.booking'].sudo().booking_logic(date1,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = request.env['project.booking'].sudo().booking_logic(date1,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
#                         booking_logic = call_booking_order(booking_logic)
                return booking_logic
            if type(booking_logic) == list:
                if booking_logic and booking_logic[0] != False:
                    booking_logic = call_booking_order_static(booking_logic)
            final_time_id = []
            return_list = []
            if type(booking_logic) != list and type(booking_logic) == dict:
                for slot_book in booking_logic.keys():
                    if type(booking_logic[slot_book]) != list:
                        slot_book_value = [booking_logic[slot_book]]
                    else:
                        slot_book_value = booking_logic[slot_book]
                    for time in slot_book_value:
                        time = request.env['time.slot.start.end'].sudo().browse([time])
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
                                              'end':time.timeslot_end_id.end_time, 'book_color': False,
                                              'end_time':  end_time, })
            return_list.append(final_time_id)
            return_list.append(date1)
            return_list.append(time_slot_based)
            return return_list
        if time_slot_based == 1:
            booking_logic = request.env['project.booking'].sudo().booking_logic_dynamic(date1,total_hours, all_anchors, project_id, sic, postal_code, slot_time)
            def call_booking_order(booking_logic):
                booking_logic = request.env['project.booking'].sudo().booking_logic_dynamic(date1,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
                if type(booking_logic) == list:
                    if booking_logic and booking_logic[0] != False:
                        booking_logic = request.env['project.booking'].sudo().booking_logic_dynamic(date1,total_hours, all_anchors, project_id, sic, postal_code, booking_logic[0])
#                         booking_logic = call_booking_order(booking_logic)
                return booking_logic
            if type(booking_logic) == list:
                if booking_logic and booking_logic[0] != False:
                    booking_logic = call_booking_order(booking_logic)
            final_time_id = []
            return_list = []
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
                        all_time = request.env['time.slot.start.end'].sudo().search([])
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
                                              'end':time.timeslot_end_id.end_time, 'book_color': False,
                                              'end_time':  end_time, })
            final_time_id = sorted(final_time_id, key=lambda k: k['start'])
            return_list.append(final_time_id)
            return_list.append(date1)
            return_list.append(time_slot_based)
            return return_list


    @http.route(['/project_create/'], type='http', auth="user", website=True)
    def project_create(self, name, **kwargs):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        project_search = request.env['project.project'].sudo().search([('partner_id','=',user_id.partner_id.id),('is_new_project','=', True)])
        for a in project_search:
            a.unlink()
        project = request.env['project.project'].sudo().with_context(created_from_user = 1).create({'name':name, 'partner_id':user_id.partner_id.id, 'is_new_project': True})
        return http.request.redirect("/booking")

    @http.route(['/booking_final'], type='http', auth="user", website=True)
    def booking_final(self, **post):
        if not post:
            return request.redirect("/booking")
        user_timeslot_id = request.env['res.users'].sudo().browse(request.uid)
        user_id = request.env['res.users'].sudo().search([('partner_id', '=', int(post['cust_id']))])
        ctx = request.context.copy()
        ctx.update({'create_from_website': True})
        create_dict = {}
        return_done = {}
        booking_id = False
        postal_code_id = False
        if post and 'pr_postal_code' in post.keys():
            postal_code_id = request.env['postal.code'].sudo().search([('name', '=', post['pr_postal_code'])])
            if not postal_code_id:
                postal_code_id = request.env['postal.code'].sudo().create({'name': post['pr_postal_code']})
            if postal_code_id:
                postal_code_id = postal_code_id.id
        location_id = request.env['location.location'].sudo().create({'postal_code': postal_code_id,
                                                                'address': post['pr_address'],
                                                                'project_id': post['pr_name']})
        if location_id:
            location_id = location_id.id
        if post and 'sic' in post.keys() and 'special' in post.keys() and post['special'] == 'special':
            if post['sic'] in ["yes", "Yes"]:
                sic = True
            else:
                sic = False
            booking_type = False
            if post['sic_request'] == str(1):
                all_anchor = []
                booking_type = 'special'
            else:
                booking_type = 'special'
            from datetime import datetime
            update_return_done = 0
            tester_id = False
            if post and 'add_accept_button' in post.keys() and post['add_accept_button'] in ['True', 'true']:
                ctx.update({'send_notification_to_testers': True})
                update_return_done = 1
                create_dict.update({'project_id': post['pr_name'], 'contact_id': post['co_name'],
                                'contact_number': post['co_no'], 'sid_required': sic,
                                'partner_id': user_id.partner_id and user_id.partner_id.id,
                                'booking_type': booking_type, 'start_date_time': datetime.strptime(post['b_date_time'], "%d-%m-%Y %H:%M:%S"),
                                'end_date_time': datetime.strptime(post['b_date_time1'], "%d-%m-%Y %H:%M:%S"), 'location_id': location_id,
                                'is_final': False, 'add_accept_button': True, 'user_tester_id': False,'user_id': user_id and user_id.id or False,'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id})
            else:
                if post.get('tester_id') and post['tester_id'] != False:
                    logging.info("_________________________%s", post.get('tester_id'));
                    tester_id = request.env['res.users'].sudo().search([('partner_id', '=', (int(eval(post['tester_id']))))])
                    logging.info("_________________________%s", tester_id);
                    if tester_id:
                        tester_id = tester_id.id
                        new_pr_id = request.env['project.project'].sudo().search([('id', '=', post['pr_name']),('is_new_project', '=', True)])
                        if sic == True  and new_pr_id:
                            tester_id.partner_id.project_ids = [(4, int(eval(post['pr_name'])))]
                create_dict.update({'project_id': post['pr_name'], 'contact_id': post['co_name'],
                                    'contact_number': post['co_no'], 'sid_required': sic,
                                    'partner_id': user_id.partner_id and user_id.partner_id.id,
                                    'booking_type': booking_type, 'start_date_time': datetime.strptime(post['b_date_time'], "%d-%m-%Y %H:%M:%S"),
                                    'end_date_time': datetime.strptime(post['b_date_time1'], "%d-%m-%Y %H:%M:%S"), 'location_id': location_id,
                                    'is_final': True, 'add_accept_button': False,'user_tester_id': tester_id,'user_id': user_id and user_id.id or False,'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id})
            booking_id = request.env['project.booking'].with_context(ctx).create(create_dict)
            local = pytz.timezone(request.context.get('tz'))
            start_datetime = datetime.strptime(booking_id.start_date_time, "%Y-%m-%d %H:%M:%S")
            start_date = local.localize(start_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            end_datetime = datetime.strptime(booking_id.end_date_time, "%Y-%m-%d %H:%M:%S")
            end_date = local.localize(end_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            booking_id.write({'start_date_time': start_date, 'end_date_time': end_date,
                              'final_start_dtime': start_date, 'final_end_dtime': end_date})
            if post['all_anchor']:
                all_anchor = post['all_anchor'].split(',')
                for an in all_anchor:
                    pr_booking_an = request.env['project.booking.anchor'].sudo().search([('id', '=', int(an))])
                    if pr_booking_an:
                        pr_booking_an.project_booking_id = booking_id and booking_id.id
            if post['sic_request'] == str(1):
                pr_booking_an = request.env['project.booking.anchor'].sudo().search([('id', '=', int(an))])
                for a in pr_booking_an:
                    a.unlink()
            return_done.update({'booking_special_done': True, 'booking_id': booking_id.booking_no,
                                    'booking_start_date': post['b_date_time'], 'booking_end_date': post['b_date_time1']})
            if post['sic_request'] == str(1):
                if post and post.get('pr_name', False):
                    ch_pr_id = request.env['project.project'].sudo().search([('id', '=', post['pr_name'])])
                    if ch_pr_id and not ch_pr_id.location_id:
                        ch_pr_id.location_id = location_id
                    if ch_pr_id:
                        ch_pr_id.is_new_project = False
            if update_return_done == 1:
                return_done.update({'show_massage_dedicated': 1})
        if post and 'sic' in post.keys() and 'special' in post.keys() and post['special'] in ['normal', 'sic_booking']:
            if post['sic'] in ["yes", "Yes"]:
                sic = True
            else:
                sic = False
            booking_type = False
            sic_required_hours = 0
            requested_time = 0
            if post['special'] == 'sic_booking':
                if post['requested_time']:
                    requested_time = "%02d.%02d" % (int(post['requested_time'].split(':')[0]), ((int(post['requested_time'].split(':')[1]) * 100) / 60))
                    requested_time = float(requested_time)
                booking_type = 'sic'
            else:
                booking_type = 'normal'
            create_dict.update({'project_id': post['pr_name'], 'contact_id': post['co_name'],
                                'contact_number': post['co_no'], 'sid_required': sic,
                                'partner_id': user_id.partner_id and user_id.partner_id.id,
                                'booking_type': booking_type, 'location_id': location_id,'sic_required_hours': requested_time,
                                'is_final': True, 'user_id': user_id and user_id.id or False,'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id})
            booking_id = request.env['project.booking'].with_context(ctx).create(create_dict)
            sic_tester_id = False
            if post['special'] == 'normal':
                if post['all_anchor']:
                    all_anchor = post['all_anchor'].split(',')
                    for an in all_anchor:
                        pr_booking_an = request.env['project.booking.anchor'].sudo().search([('id', '=', int(an))])
                        if pr_booking_an:
                            pr_booking_an.project_booking_id = booking_id and booking_id.id
            if type(eval(post['tm_id'])) == tuple:
                time_slot_booking_id_all = request.env['timeslot.booking'].sudo().search([('id', 'in', list(eval(post['tm_id'])))])
                for time_slot_booking_id in time_slot_booking_id_all:
                    time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                    booking_id.user_tester_id = time_slot_booking_id.tester_id
                    time_slot_booking_id.temp = False
                    if post['special'] == 'sic_booking':
                        sic_tester_id = time_slot_booking_id.tester_id
            else:
                time_slot_booking_id = request.env['timeslot.booking'].sudo().search([('id', '=', post['tm_id'])])
                if time_slot_booking_id:
                    time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                    booking_id.user_tester_id = time_slot_booking_id.tester_id
                    time_slot_booking_id.temp = False
                    if post['special'] == 'sic_booking':
                        sic_tester_id = time_slot_booking_id.tester_id
            if sic_tester_id:
                sic_tester_id.partner_id.project_ids = [(4, int(eval(post['pr_name'])))]
            time_slot_booking = request.env['timeslot.booking'].sudo().search([('user_id', '=', user_timeslot_id and user_timeslot_id.id), ('temp', '=', True)], order="id desc")
            if time_slot_booking:
                for tm in time_slot_booking:
                    tm.unlink()
            return_done.update({'booking_done': True, 'booking_id': booking_id.booking_no,
                                    'booking_date': post['b_date'], 'booking_time': post['b_time']})
#         if post and 'sic_req' in post.keys():
#             sic = True
#             booking_type = 'sic'
#             if post.get('tester_id'):
#                 tester_id = request.env['res.users'].sudo().search([('partner_id', '=', (int(eval(post['tester_id']))))])
#                 tester_id.partner_id.project_ids = [(4, int(eval(post['pr_name'])))]
#             else:
#                 tester_id = False
#             from datetime import datetime
#             create_dict.update({'project_id': post['pr_name'], 'contact_id': post['co_name'],
#                                 'contact_number': post['co_no'], 'sid_required': sic,
#                                 'partner_id': user_id.partner_id and user_id.partner_id.id,
#                                 'booking_type': booking_type, 'start_date_time': datetime.strptime(post['b_date_time'], "%d-%m-%Y %H:%M:%S"),
#                                 'end_date_time': datetime.strptime(post['b_date_time1'], "%d-%m-%Y %H:%M:%S"), 'user_tester_id': tester_id and tester_id.id,'location_id': location_id,
#                                 'is_final': True, 'user_id': user_id and user_id.id or False,'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id})
#             booking_id = request.env['project.booking'].with_context(ctx).create(create_dict)
#             local = pytz.timezone(request.context.get('tz'))
#             start_datetime = datetime.strptime(booking_id.start_date_time, "%Y-%m-%d %H:%M:%S")
#             start_date = local.localize(start_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#             end_datetime = datetime.strptime(booking_id.end_date_time, "%Y-%m-%d %H:%M:%S")
#             end_date = local.localize(end_datetime, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#             booking_id.write({'start_date_time': start_date, 'end_date_time': end_date,
#                               'final_start_dtime': start_date, 'final_end_dtime': end_date})
#             return_done.update({'booking_sic_done': True, 'booking_id': booking_id.booking_no,
#                                     'booking_start_date': post['b_date_time'], 'booking_end_date': post['b_date_time1']})
        if post and post.get('pr_name', False):
            ch_pr_id = request.env['project.project'].sudo().search([('id', '=', post['pr_name'])])
            if ch_pr_id and not ch_pr_id.location_id:
                ch_pr_id.location_id = location_id
            if ch_pr_id:
                ch_pr_id.is_new_project = False
        return http.request.render("hilti_modifier_customer_booking.customer_booking_template", return_done)


