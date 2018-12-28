from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
import werkzeug
import json
import base64
import os
from random import randint
import datetime

class HiltiBooking(http.Controller):
    
    @http.route(['/booking'], type='http', auth="user", website=True)
    def customer_booking(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        master_ids = request.env['anchor.type'].sudo().search([])
        #master_size_ids = request.env['anchor.size'].sudo().search([])
        is_new_pr = 0
        project_id = request.env['project.project'].sudo().search([], order="id desc")
        new_pr_id = request.env['project.project'].sudo().search([('is_new_project', '=', True),('partner_id','=', user_id.partner_id.id)])
        if new_pr_id:
            is_new_pr = 1
        return http.request.render("hilti_modifier_customer_booking.customer_booking_template", {'project_id': project_id, 'is_new_pr': is_new_pr, 'master_ids': master_ids, 'master_size_ids': []})
    
    
    @http.route(['/check_project_is_new'], type='json', auth="user", website=True)
    def check_project_is_new(self, **post):
        temp = 0
        if post and post['project_id']:
            new_pr_id = request.env['project.project'].sudo().search([('id', '=', post['project_id']),('is_new_project', '=', True)])
            if new_pr_id:
                temp = 1
        return temp
    
    
    @http.route(['/get_anchor_size'], type='json', auth="user", website=True)
    def get_anchor_size(self, **post):
        an_id = post['selected_id']
        anchor_master = request.env['anchor.master'].sudo().search([('anchor_type_id', '=', int(an_id))])
        anchor_size = []
        image1 = []
        image2 = []
        image3 = []
        if anchor_master:
            image1.append(anchor_master.simple_image)
            image2.append(anchor_master.medium_image)
            image3.append(anchor_master.complex_image)
            for size in anchor_master.anchor_size_id:
                anchor_size.append({'id': size.id, 'name': size.name})
        return [anchor_size, image1, image2, image3]
    
    @http.route(['/my_booking'], type='http', auth="user", website=True)
    def my_booking(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_company', 'menu_my_booking')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_company', 'action_my_booking_view')[1]
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
                                                                                 'anchor_size_id': post.get('an_type'),
                                                                                 'anchor_qty': post.get('an_qty'), 
                                                                                 'an_complexity': post.get('redio_val'),
                                                                                 'name': post.get('an_name')})
        return pr_booking_an.id
    
        
    @http.route(['/create_time_slot'], type='json', auth="user", website=True)
    def create_time_slot(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        if post and 'date' in post.keys() and 'time_slot_id' in post.keys():
            time_slot_booking_record = request.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
            if time_slot_booking_record:
                for tm in time_slot_booking_record:
                    tm.unlink()
            time_slot_booking = request.env['timeslot.booking'].sudo().create({'time_slot_id': post.get('time_slot_id'), 'user_id': user_id and user_id.id, 'booking_date': post.get('date'), 'temp': True})
        return True
    
    
    @http.route(['/user_book_slot'], type='json', auth="user", website=True)
    def user_book_slot(self, **post):
        booking_record = []
        user_id = request.env['res.users'].sudo().browse(request.uid)
        time_slot_booking = request.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
        if time_slot_booking and time_slot_booking[0]:
            start = int(time_slot_booking[0].timeslot_start_id.start_time)
            end = int(time_slot_booking[0].timeslot_end_id.end_time)
            start_time = "%02d:%02d" % (start, int(str(time_slot_booking[0].timeslot_start_id.start_time - start).split('.')[1]))
            end_time = "%02d:%02d" % (end, int(str(time_slot_booking[0].timeslot_end_id.end_time - end).split('.')[1]))
            if start > 12:
                start = (start - 12)
                start_time = "%02d:%02d" % (start, int(str(time_slot_booking[0].timeslot_start_id.start_time - (start + 12)).split('.')[1]))
            if end > 12:
                end = (end - 12)
                end_time = "%02d:%02d" % (end, int(str(time_slot_booking[0].timeslot_end_id.end_time - (end + 12)).split('.')[1]))
            booking_record.append({'start':time_slot_booking[0].timeslot_start_id.start_time,
                                      'start_time':  start_time,
                                      'Booking_date': datetime.datetime.strptime(time_slot_booking[0].booking_date, '%Y-%m-%d').strftime('%d-%m-%Y'),
                                      'end':time_slot_booking[0].timeslot_end_id.end_time,
                                      'end_time':  end_time, 'time_slot_booking': time_slot_booking[0] and time_slot_booking[0].id})
        else:
            booking_record.append({'start': False,
                                      'start_time':  False,
                                      'Booking_date': False,
                                      'end':False,
                                      'end_time':  False,
                                      'time_slot_booking': False})
        return booking_record
        
    @http.route(['/all_slot'], type='json', auth="user", website=True)
    def all_slot(self, date, cellMonth, cellYear, **post):
        date1 = '%d-%02d-%02d' % (cellYear, cellMonth, date)
        time_slot = request.env['timeslot.master'].sudo().search([], limit=1)
        book_ids = request.env['timeslot.booking'].sudo().search([('booking_date', '=', date1)])
        booking_time_ids = [time.id for time in time_slot.time_slot_ids for a in book_ids if a.timeslot_start_id == time.timeslot_start_id and a.timeslot_end_id == time.timeslot_end_id]
        final_time_id = []
        return_list = []
        for time in time_slot.time_slot_ids:
            start = int(time.timeslot_start_id.start_time)
            end = int(time.timeslot_end_id.end_time)
            start_time = "%02d:%02d" % (start, int(str(time.timeslot_start_id.start_time - start).split('.')[1]))
            end_time = "%02d:%02d" % (end, int(str(time.timeslot_end_id.end_time - end).split('.')[1]))
            if start > 12:
                start = (start - 12)
                start_time = "%02d:%02d" % (start, int(str(time.timeslot_start_id.start_time - (start + 12)).split('.')[1]))
            if end > 12:
                end = (end - 12)
                end_time = "%02d:%02d" % (end, int(str(time.timeslot_end_id.end_time - (end + 12)).split('.')[1]))
            if time.id in booking_time_ids:
                final_time_id.append({'start':time.timeslot_start_id.start_time,
                                      'start_time':  start_time,
                                      'time_slot_id': time.id,
                                      'end':time.timeslot_end_id.end_time, 'book_color': True,
                                      'end_time':  end_time, })
            else:
                final_time_id.append({'start':time.timeslot_start_id.start_time,
                                      'start_time':  start_time,
                                      'time_slot_id': time.id,
                                      'end':time.timeslot_end_id.end_time, 'book_color': False,
                                      'end_time':  end_time, })
        return_list.append(final_time_id)
        return_list.append(date1)
        return return_list
        
    @http.route(['/project_create/'], type='http', auth="user", website=True)
    def project_create(self, name, **kwargs):
        user_id = request.env['res.users'].sudo().browse(request.uid)
        new_pr_id = request.env['project.project'].sudo().search([('partner_id', '=', user_id.partner_id.id), ('is_new_project', '=', True)])
        if new_pr_id:
            for pr in new_pr_id:
                pr.is_new_project = False
        project = request.env['project.project'].sudo().create({'name':name, 'partner_id':user_id.partner_id.id, 'is_new_project': True})
        request.render("hilti_modifier_customer_booking.customer_booking_template", dict())
        
    @http.route(['/booking_final'], type='http', auth="user", website=True)
    def booking_final(self, **post):
        user_id = request.env['res.users'].sudo().browse(request.uid)
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
            if post['sic'] == "yes":
                sic = True
            else:
                sic = False
            booking_type = False
            if post['sic_request'] == str(1):
                booking_type = 'sic'
            else:
                booking_type = 'special'
            create_dict.update({'project_id': post['pr_name'], 'contact_id': post['co_name'],
                                'contact_number': post['co_no'], 'sid_required': sic,
                                'partner_id': user_id.partner_id and user_id.partner_id.id,
                                'booking_type': booking_type, 'start_date_time': post['b_date_time'],
                                'end_date_time': post['b_date_time1'], 'location_id': location_id,
                                'is_final': True, 'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id})
            booking_id = request.env['project.booking'].sudo().with_context(ctx).create(create_dict)
            if post['all_anchor']:
                all_anchor = post['all_anchor'].split(',')
                for an in all_anchor:
                    pr_booking_an = request.env['project.booking.anchor'].sudo().search([('id', '=', int(an))])
                    if pr_booking_an:
                        pr_booking_an.project_booking_id = booking_id and booking_id.id
            return_done.update({'booking_special_done': True, 'booking_id': booking_id.booking_no,
                                    'booking_start_date': post['b_date_time'], 'booking_end_date': post['b_date_time1']})
        if post and 'sic' in post.keys() and 'special' in post.keys() and post['special'] == 'normal':
            if post['sic'] == "yes":
                sic = True
            else:
                sic = False
            booking_type = False
            if post['sic_request'] == str(1):
                booking_type = 'sic'
            else:
                booking_type = 'normal'
            create_dict.update({'project_id': post['pr_name'], 'contact_id': post['co_name'],
                                'contact_number': post['co_no'], 'sid_required': sic,
                                'partner_id': user_id.partner_id and user_id.partner_id.id,
                                'booking_type': booking_type, 'location_id': location_id,
                                'is_final': True, 'company_id': user_id.partner_id and user_id.partner_id.parent_id and user_id.partner_id.parent_id.id})
            booking_id = request.env['project.booking'].sudo().with_context(ctx).create(create_dict)
            if post['all_anchor']:
                all_anchor = post['all_anchor'].split(',')
                for an in all_anchor:
                    pr_booking_an = request.env['project.booking.anchor'].sudo().search([('id', '=', int(an))])
                    if pr_booking_an:
                        pr_booking_an.project_booking_id = booking_id and booking_id.id
            time_slot_booking_id = request.env['timeslot.booking'].sudo().search([('id', '=', post['tm_id'])])
            if time_slot_booking_id:
                time_slot_booking_id.pr_booking_id = booking_id and booking_id.id
                time_slot_booking_id.temp = False
            time_slot_booking = request.env['timeslot.booking'].sudo().search([('user_id', '=', user_id and user_id.id), ('temp', '=', True)], order="id desc")
            if time_slot_booking:
                for tm in time_slot_booking:
                    tm.unlink()
            return_done.update({'booking_done': True, 'booking_id': booking_id.booking_no,
                                    'booking_date': post['b_date'], 'booking_time': post['b_time']})
        if post and post.get('pr_name', False):
            ch_pr_id = request.env['project.project'].sudo().search([('id', '=', post['pr_name'])])
            if ch_pr_id:
                ch_pr_id.is_new_project = False
        return http.request.render("hilti_modifier_customer_booking.customer_booking_template", return_done)
    
    
