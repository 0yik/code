# -*- encoding: utf-8 -*-

import odoo
import odoo.modules.registry
import ast

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home

import datetime
import json
import pytz
import os
from odoo.addons.website_payment.controllers.main import WebsitePayment
import logging

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------

class AdminRegister(Home):

    def send_student_mail(self, student_id):
        template_id = request.env.ref('online_school_enrollment.student_registration_template_id')
        template_id.sudo().email_to = student_id.email
        template_id.sudo().email_from = ''
        template_id.sudo().send_mail(student_id.id, force_send=True)

    @http.route('/print_student_report', type='http', auth="public", website=True, csrf=False)
    def print_student_report(self, **post):
        if post.get('student_report'):
            without_paypal = post.get('without_paypal')
            if not without_paypal:
                tx_id = request.env['payment.transaction'].sudo().browse(int(post.get('student_report')))
                pdf = request.env['report'].sudo().with_context(set_viewport_size=True).get_pdf([tx_id.sudo().student_id.id], 'online_school_enrollment.student_report')
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
                return request.make_response(pdf, headers=pdfhttpheaders)
            if without_paypal:
                pdf = request.env['report'].sudo().with_context(set_viewport_size=True).get_pdf([int(post.get('student_report'))], 'online_school_enrollment.student_report')
                print
                pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
                return request.make_response(pdf, headers=pdfhttpheaders)
    
    @http.route('/filter_data', type='http', auth="public", website=True, csrf=False)
    def filter_data(self, **post):
        filter_standard_ids = []
        result = {'standard_ids': []}
        if post.get('school_id'):
            school_id = request.env['school.school'].sudo().browse(int(post.get('school_id')))
            if school_id.standards:
                for course in school_id.standards:
                    result['standard_ids'].append({'name':course.standard_id.name + ' [' + course.division_id.name + ']' , 'id':course.id })
        return json.dumps(result)

    @http.route('/enrolment', type='http', auth="public", website=True)
    def admission_register(self, **post):
        values = {}
        school_ids = request.env['school.school'].sudo().search([], order="name asc")
        courses_ids = request.env['school.standard'].sudo().search([], order="course_name asc")
        intake_ids = request.env['academic.year'].sudo().search([], order="name asc")
        state_ids = request.env['res.country.state'].sudo().search([])
        country_ids = request.env['res.country'].sudo().search([])
        mother_tongue_ids = request.env['mother.toungue'].sudo().search([])
        relation_ids = request.env['student.relation.master'].sudo().search([])
        values.update({'school_ids':school_ids,
            'standard_ids': courses_ids,
            'year_ids':intake_ids,
            'state_ids':state_ids,
            'country_ids':country_ids,
            'mother_tongue_ids':mother_tongue_ids,
            'relation_ids':relation_ids,
            })
        return request.render('online_school_enrollment.admission_register_form', values)

    @http.route(['/admission/register/create'], type='http', auth="public", website=True, csrf=False)
    def admission_register_create(self, **post):
        vals = {}
        values = {}
        parent_vals = {}
        previous_school_vals = {}
        family_detail_vals = {}
        if post:
            student_parent_id = False
            dob = False
            if post.get('dob',False):
                dob = datetime.datetime.strptime(str(post.get('dob',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
            admission_date = datetime.datetime.strptime(str(datetime.datetime.today().date()), "%Y-%m-%d").strftime('%m/%d/%Y')
            pid = request.env['ir.sequence'].sudo().next_by_code('student.student')
            # Student registration
            # if post.get('first_name',False):
                # first_name = post.get('first_name').split(' ')
                # middle = ''
                # first = ''
                # last = ''
                # first = first_name and first_name[0] or ''
                # middle = first_name and len(first_name) == 2 and first_name[1] or ''
                # last = first_name and len(first_name) == 3 and first_name[2] or ''
            vals.update({
                'pid':pid,
                'name': post.get('first_name',False) or '',
                # 'middle': str(middle) or '',
                # 'last': str(last) or '',
                'gender': post.get('gender',False),
                'school_id':post.get('school_ids',False) and int(post.get('school_ids',False)),
                'standard_id':post.get('standard_ids',False) and int(post.get('standard_ids',False)),
                'year':post.get('year_ids',False) and int(post.get('year_ids',False)),
                'street':post.get('address1',False),
                'street2':post.get('address2',False),
                'city':post.get('city',False),
                'state_id':post.get('state_ids',False) and int(post.get('state_ids',False)),
                'zip':post.get('zip',False),
                'country_id':post.get('country_ids',False) and int(post.get('country_ids',False)),
                'phone':post.get('phone',False),
                'mobile':post.get('mobile',False),
                'email':post.get('email',False),
                'website':post.get('website',False),
                'date_of_birth':dob,
                'admission_date':admission_date,
                'contact_phone1':post.get('phone_no',False),
                'contact_mobile1':post.get('mobile_no',False),
                'maritual_status': post.get('marital_status',False),
                'remark': post.get('qualification_remark',False),
                'mother_tongue': post.get('mother_tongue_ids',False) and int(post.get('mother_tongue_ids',False)),
                'active':True,
                })
            already_student_id = request.env['student.student'].sudo().search([
                ('email','=',post.get('email',False)),
                ('mobile','=',post.get('mobile',False)),
                ('phone','=',post.get('phone',False)),
                ('date_of_birth','=',dob),
                ('contact_phone1','=',post.get('phone_no',False)),
                ('contact_mobile1','=',post.get('mobile_no',False)),
                ('active','=',True),
                ],limit=1)
            student_register_id = False
            if not already_student_id:
                student_register_id = request.env['student.student'].sudo().create(vals)
                student_register_id.active = True            
            # Student Payment Detail
            if post.has_key('payment_option') and post.get('payment_option',False) == 'manually':
                self.send_student_mail(already_student_id or student_register_id)
                values.update({'tx_id':(already_student_id and already_student_id.id or student_register_id and student_register_id.id), 'without_paypal':True})
                return request.render("online_school_enrollment.thanks", values)
        return request.render('website.404')