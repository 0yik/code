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
from odoo.addons.school_enrolment_paypal.controllers.main import AdminRegister
import logging
import json

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------

class AdminRegister(AdminRegister):

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
        family_detail_student_ids = request.env['student.student'].sudo().search([])
        highest_qualification_id = request.env['highest.qualification'].sudo().search([])
        general_survey_id = request.env['general.survey'].sudo().search([])
        values.update({'school_ids':school_ids,
            'standard_ids': courses_ids,
            'year_ids':intake_ids,
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
                student_parent_id = False
                already_parent_id = request.env['res.partner'].sudo().search([
                    ('name','=',post.get('parent_name',False)),
                    ('email','=',post.get('parent_email',False)),
                    ('phone','=',post.get('parent_phone',False)),
                    ],limit=1)
                if not already_parent_id:
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

                if already_parent_id or student_parent_id:
                    vals.update({
                        'parent_id':[(6,0,((already_parent_id and already_parent_id.ids) or (student_parent_id and student_parent_id.ids or [])))],
                        })
            # Student registration
            # if post.get('first_name',False):
            #     first_name = post.get('first_name').split(' ')
            #     middle = ''
            #     first = ''
            #     last = ''
            #     first = first_name and first_name[0] or ''
            #     middle = first_name and len(first_name) == 2 and first_name[1] or ''
            #     last = first_name and len(first_name) == 3 and first_name[2] or ''
            highest_qualification_id = False
            if post.get('highest_qualification_id',False):
                if post.get('highest_qualification_id') == 'select_highest_qualification':
                    highest_qualification_id = False
                else:
                    highest_qualification_id = post.get('highest_qualification_id')
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
                'nric':post.get('nric',False),
                'maritual_status': post.get('marital_status',False),
                'hp_no':post.get('hp_no',False),
                'occupation': post.get('occupation',False),
                'income':post.get('income',False),
                'highest_qualification_id': highest_qualification_id or False,
                'general_survey_id': post.get('general_survey_id',False) and int(post.get('general_survey_id',False)),
                'citizenship': post.get('citizenship',False),
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
            # Student Reference Detail
            if post.get('reference_name',False) and \
                post.get('reference_phone',False) and \
                post.get('reference_designation',False):
                first_name = post.get('reference_name',False).split(' ')
                middle = ''
                first = ''
                last = ''
                first = first_name and first_name[0] or ''
                middle = first_name and len(first_name) == 2 and first_name[1] or ''
                last = first_name and len(first_name) == 3 and first_name[2] or ''
                parent_vals.update({
                    'name': first,
                    'middle': middle,
                    'phone': post.get('reference_phone',False),
                    'last':last or ' ',
                    'designation':post.get('reference_designation',False),
                    'gender': post.get('reference_gender',False),
                    'reference_id':already_student_id and already_student_id.id or student_register_id and student_register_id.id,
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
                    'family_contact_id':already_student_id and already_student_id.id or student_register_id and student_register_id.id,
                    })
                family_detail_contact_id = request.env['student.family.contact'].sudo().create(family_detail_vals)
            
            # Student Education BackgroUnd
            if post.get('eb_institution',False) and \
                post.get('eb_from_date',False) and post.get('eb_to_date',False):
                eb_from_date = False
                eb_to_date = False
                count = 0
                post_from_ascii = [ord(c) for c in str(post.get('eb_from_date',False))]
                post_to_ascii = [ord(c) for c in str(post.get('eb_to_date',False))]
                for i in post_from_ascii + post_to_ascii:
                    if i not in [49, 50, 51, 52, 53, 54, 55, 56, 57, 48, 47]:
                        post['eb_from_date'] = False
                        post['eb_to_date'] = False
                if post.get('eb_from_date',False):
                    eb_from_date = datetime.datetime.strptime(str(post.get('eb_from_date',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
                if post.get('eb_to_date',False):
                    eb_to_date = datetime.datetime.strptime(str(post.get('eb_to_date',False)), "%m/%d/%Y").strftime('%m/%d/%Y')
                vals = {
                    'institution': post.get('eb_institution',False),
                    'from_date': eb_from_date,
                    'to_date': eb_to_date,
                    'achievement':str(post.get('eb_achievement',False)),
                    'student_id':already_student_id and already_student_id.id or student_register_id and student_register_id.id,
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
                        'student_id':already_student_id and already_student_id.id or student_register_id and student_register_id.id,
                    }
                    education_background_id = request.env['education.background'].sudo().create(value)
            # Student Payment Detail
            if post.has_key('payment_option') and post.get('payment_option',False) != 'manually':
                if post.get('school_ids',False) and int(post.get('school_ids',False)) and (already_student_id or student_register_id):
                    self.send_student_mail(already_student_id or student_register_id)
                    school_ids = post.get('school_ids',False) and int(post.get('school_ids',False))
                    school_browse_ids = request.env['school.school'].sudo().browse(school_ids)
                    amount = 0
                    if school_browse_ids.application_fee_id:
                        env = request.env
                        user = env.user.sudo()
                        currency_id = user.company_id.currency_id.id
                        country_id = user.company_id.country_id.id
                        for line in school_browse_ids.application_fee_id.line_ids:
                            if line.type == 'application_fee':
                                values.update({'amount':line.amount,'name': line.name})
                        reference = (already_student_id and already_student_id.name +'-'+ school_browse_ids.name + '-' +  str(already_student_id.nric or '') + '-' + str(already_student_id.id)) or (student_register_id.name +'-'+ school_browse_ids.name + '-' + str(student_register_id.nric or '') + '-' + str(student_register_id.id))
                        amount = values.get('amount', False)
                        partner_id = False
                        acquirer_id = False
                        partner_id = already_student_id and already_student_id.user_id.partner_id.id or student_register_id.user_id.partner_id.id
                        currency = env['res.currency'].browse(currency_id)
                        # Try default one then fallback on first
                        acquirer_id = acquirer_id and int(acquirer_id) or \
                            env['ir.values'].get_default('payment.transaction', 'acquirer_id', company_id=user.company_id.id) or \
                            env['payment.acquirer'].search([('website_published', '=', True), ('company_id', '=', user.company_id.id)])[0].id
                        acquirer = env['payment.acquirer'].with_context(submit_class='btn btn-primary pull-right',
                                                                        submit_txt=_('Pay Now')).browse(acquirer_id)
                        # auto-increment reference with a number suffix if the reference already exists
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        payment_form = acquirer.sudo().render(reference, float(amount), currency.id, values={'return_url': '/website_payment/confirm', 'partner_id': partner_id})
                        
                        values = {
                            'reference': reference,
                            'acquirer': acquirer,
                            'currency': currency,
                            'amount': float(amount),
                            'payment_form': payment_form,
                            'partner_id':partner_id or False,
                            'student_register_id': student_register_id,
                            'student_id':already_student_id and already_student_id.id or student_register_id.id,
                        }
                        return request.render('school_enrolment_paypal.admission_payment', values)
                    else:
                        return request.render('website.404')
            else:
                self.send_student_mail(already_student_id or student_register_id)
                values.update({'tx_id':already_student_id.id  or student_register_id.id, 'without_paypal':True})
                return request.render("online_school_enrollment.thanks", values)         
        return request.render('website.404')

    @http.route(['/api/register/get_intake_item'], auth='public', csrf=False)
    def check_promo_code(self, **post):
        data = json.loads(post.items()[0][0])
        course_id = int(data['course_id'])
        intake_ids = request.env['academic.year'].sudo().search([('standard_id','=',course_id)], order="name asc")
        res = []
        for intake_id in intake_ids:
            vals = {}
            vals.update({
                'id'   : intake_id and intake_id.id,
                'name' : intake_id and intake_id.name,
            })
            res.append(vals)
        return json.dumps(res);
