# -*- encoding: utf-8 -*-

import odoo
import odoo.modules.registry
import ast

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home

import datetime
import json
import pytz

#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------
class AdminRegister(Home):

    
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
        school_ids = request.env['school.school'].sudo().search([])
        courses_ids = request.env['school.standard'].sudo().search([])
        intake_ids = request.env['academic.year'].sudo().search([])
        # division_ids = request.env['standard.division'].sudo().search([])
        state_ids = request.env['res.country.state'].sudo().search([])
        country_ids = request.env['res.country'].sudo().search([])
        mother_tongue_ids = request.env['mother.toungue'].sudo().search([])
        relation_ids = request.env['student.relation.master'].sudo().search([])
        family_detail_student_ids = request.env['student.student'].sudo().search([])
        highest_qualification_id = request.env['highest.qualification'].sudo().search([])
        general_survey_id = request.env['general.survey'].sudo().search([])
        values.update({'school_ids':school_ids,
            'standard_ids': courses_ids,
            'year_ids':intake_ids,
            # 'division_ids':division_ids,
            'state_ids':state_ids,
            'country_ids':country_ids,
            'mother_tongue_ids':mother_tongue_ids,
            'relation_ids':relation_ids,
            'family_detail_student_ids':family_detail_student_ids,
            'highest_qualification_id': highest_qualification_id,
            'general_survey_id':general_survey_id,
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
            # Parent Detail
            if post.get('parent_name',False) and post.get('parent_city',False) and \
                post.get('parent_state_ids',False) and post.get('parent_country_ids',False) and \
                post.get('parent_email',False):
                parent_vals.update({
                    'type':'contact',
                    'parent_school':True,
                    'name': post.get('parent_name',False),
                    'city': post.get('parent_city',False),
                    'state_id':post.get('parent_state_ids',False) and int(post.get('parent_state_ids',False)),
                    'country_id':post.get('parent_country_ids',False) and int(post.get('parent_country_ids',False)),
                    'phone':post.get('parent_phone',False),
                    'email':post.get('parent_email',False),
                    })
                student_parent_id = request.env['res.partner'].sudo().create(parent_vals)
                if student_parent_id:
                    vals.update({
                        'parent_id':[(6,0,student_parent_id and student_parent_id.ids or [])],
                        })
            # Student registration
            if post.get('first_name',False):
                first_name = post.get('first_name').split(' ')
                middle = ''
                first = ''
                last = ''
                print "first_name--------------",first_name,len(first_name)
                # if len(first_name) >= 2:
                first = first_name and first_name[0] or ''
                middle = first_name and len(first_name) == 2 and first_name[1] or ''
                last = first_name and len(first_name) == 3 and first_name[2] or ''
            vals.update({
                'pid':pid,
                'name': str(first) or '',
                'middle': str(middle) or '',
                'last': str(last) or '',
                'gender': post.get('gender',False),
                'school_id':post.get('school_ids',False) and int(post.get('school_ids',False)),
                'standard_id':post.get('standard_ids',False) and int(post.get('standard_ids',False)),
                # 'division_id':post.get('division_ids',False) and int(post.get('division_ids',False)),
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
                'nric':post.get('nric',False),
                'maritual_status': post.get('marital_status',False),
                'hp_no':post.get('hp_no',False),
                'occupation': post.get('occupation',False),
                'income':post.get('income',False),
                'highest_qualification_id': post.get('highest_qualification_id',False) and int(post.get('highest_qualification_id',False)),
                'general_survey_id': post.get('general_survey_id',False) and int(post.get('general_survey_id',False)),
                'citizenship': post.get('citizenship',False),
                'remark': post.get('qualification_remark',False),
                'mother_tongue': post.get('mother_tongue_ids',False) and int(post.get('mother_tongue_ids',False)),
                })
            student_register_id = request.env['student.student'].sudo().create(vals)
            # Student Reference Detail
            if post.get('reference_name',False) and \
                post.get('reference_middle_name',False) and post.get('reference_phone',False) and \
                post.get('reference_last_name',False) and post.get('reference_designation',False):
                first_name = post.get('reference_name',False).split(' ')
                middle = ''
                first = ''
                last = ''
                if len(first_name) >= 2:
                    first = first_name[0]
                    middle = first_name[1]
                    last = first_name[2]
                parent_vals.update({
                    'name': first,
                    'middle': middle,
                    'phone': post.get('reference_phone',False),
                    'last':last,
                    'designation':post.get('reference_designation',False),
                    'gender': post.get('reference_gender',False),
                    'reference_id':student_register_id and student_register_id.id,
                    })
                student_reference_id = request.env['student.reference'].sudo().create(parent_vals)
            # Student Family Detail
            if post.get('family_detail_related_student',False) and \
                post.get('family_detail_phone',False) and post.get('family_detail_relation_ids',False):
                family_detail_vals.update({
                    'rel_name': post.get('family_detail_related_student',False),
                    'phone': post.get('family_detail_phone',False),
                    'relation': post.get('family_detail_relation_ids',False),
                    'email':post.get('family_detail_email',False),
                    'stu_name':post.get('family_detail_student_ids',False),
                    'name': post.get('family_detail_student_new_name',False),
                    'family_contact_id':student_register_id and student_register_id.id,
                    })
                family_detail_contact_id = request.env['student.family.contact'].sudo().create(family_detail_vals)
            # Student Education BackgroUnd
            if post.get('eb_institution',False) and \
                post.get('eb_from_date',False) and post.get('eb_to_date',False):
                eb_from_date = False
                eb_to_date = False
                count = 0
                if post.get('eb_from_date',False):
                    eb_from_date = datetime.datetime.strptime(str(post.get('eb_from_date',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
                if post.get('eb_to_date',False):
                    eb_to_date = datetime.datetime.strptime(str(post.get('eb_to_date',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
                vals = {
                    'institution': post.get('eb_institution',False),
                    'from_date': eb_from_date,
                    'to_date': eb_to_date,
                    'achievement':str(post.get('eb_achievement',False)),
                    'student_id':student_register_id and student_register_id.id,
                    }
                education_background_id = request.env['education.background'].sudo().create(vals)
                while (count < int(post.get('total_line', 0))):
                    if post.get("eb_from_date_"+str(count),False):
                        eb_from_date = datetime.datetime.strptime(str(post.get("eb_from_date_"+str(count),False)), "%m/%d/%Y").strftime('%m/%d/%Y')
                    if post.get("eb_to_date_"+str(count),False):
                        eb_to_date = datetime.datetime.strptime(str(post.get("eb_to_date_"+str(count),False)), "%m/%d/%Y").strftime('%m/%d/%Y')
                    count = count + 1
                    value = {
                        "institution":post.get("eb_institution_"+str(count),False),
                        "from_date":eb_from_date,
                        "to_date":eb_to_date,
                        "achievement":post.get("eb_achievement_"+str(count),False),
                        'student_id':student_register_id and student_register_id.id,
                    }
                    education_background_id = request.env['education.background'].sudo().create(value)
            # Student Fee Receipt
            # if student_register_id:
            #     if post.get('payment_option',False):
            #         payslip_detail_vals = {}
            #         if post.get('payment_option',False) == 'manually':
            #             school_id = False
            #             number = request.env['ir.sequence'].sudo().next_by_code('student.payslip')
            #             school_ids = post.get('school_ids',False) and int(post.get('school_ids',False)) 
            #             student_fees_structure_ids = request.env['student.fees.structure'].sudo().search([('name','ilike','Application Fees Structure')])
            #             if school_ids:
            #                 school_id = request.env['school.school'].sudo().browse(school_ids)
            #             payslip_detail_vals.update({
            #                 'student_id': student_register_id and student_register_id.id,
            #                 'type': 'out_invoice',
            #                 'fees_structure_id': student_fees_structure_ids and student_fees_structure_ids[0].id or 1,
            #                 'number':number or False,
            #                 'standard_id': student_register_id.standard_id.id,
            #                 'company_id': school_id and school_id.id or 1,
            #                 })
            #             payslip_id = request.env['student.payslip'].sudo().create(payslip_detail_vals)
            # Student Previous School Detail
            # if post.get('previous_school_name',False) and \
            #     post.get('previous_school_registration_no',False) and post.get('previous_school_standard_ids',False):
            #     previous_school_admission_date = False
            #     previous_school_exit_date = False
            #     if post.get('previous_school_admission_date',False):
            #         previous_school_admission_date = datetime.datetime.strptime(str(post.get('previous_school_admission_date',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
            #     if post.get('previous_school_exit_date',False):
            #         previous_school_exit_date = datetime.datetime.strptime(str(post.get('previous_school_exit_date',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
            #     previous_school_vals.update({
            #         'name': post.get('previous_school_name',False),
            #         'registration_no': post.get('previous_school_registration_no',False),
            #         'course_id': post.get('previous_school_standard_ids',False),
            #         'admission_date':previous_school_admission_date,
            #         'exit':previous_school_exit_date,
            #         'previous_school_id':student_register_id and student_register_id.id,
            #         })
            #     previous_school_id = request.env['student.previous.school'].sudo().create(previous_school_vals)
            # Student Payment Detail
            if post.has_key('payment_option') and post.get('payment_option',False) != 'manually':
                if post.get('school_ids',False) and int(post.get('school_ids',False)) and student_register_id:
                    school_ids = post.get('school_ids',False) and int(post.get('school_ids',False))
                    school_browse_ids = request.env['school.school'].sudo().browse(school_ids)
                    amount = 0
                    if school_browse_ids.application_fee_id:
                        payment_ids = request.env['payment.acquirer'].search([('provider','=','paypal')])
                        payment_url = payment_ids[0].sudo().paypal_get_form_action_url()
                        for line in school_browse_ids.application_fee_id.line_ids:
                            if line.type == 'application_fee':
                                values.update({'amount':line.amount,'name': line.name, 'url':payment_url})
                        return request.render("online_school_enrollment.school_payment", values)
                    else:
                        return request.render('website.404')
            else:
                return request.render("online_school_enrollment.thanks", values)         
        return request.render('website.404')
    