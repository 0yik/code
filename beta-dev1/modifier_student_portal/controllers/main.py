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
from odoo.addons.student_portal.controllers.main import StudentPortal
import logging

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------

class StudentPortal(StudentPortal):

    # Main student Portal Profile 
    @http.route(['/student/portal/profile'], type='http', auth="user", website=True)
    def student_portal_profile(self, **kw):
        partner = request.env.user.partner_id
        student_id = request.env['student.student'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
        country_ids = request.env['res.country'].sudo().search([])
        state_ids = request.env['res.country.state'].sudo().search([])
        mother_tongue_ids = request.env['mother.toungue'].sudo().search([])
        general_survey_ids = request.env['general.survey'].sudo().search([])
        highest_qualification_ids = request.env['highest.qualification'].sudo().search([])
        values = {'student_profile': student_id,
                'gender':student_id.gender,
                'school_ids':student_id.sudo().school_id,
                'standard_ids': student_id.sudo().standard_id,
                'year_ids': student_id.sudo().year,
                'country_id': student_id.sudo().country_id,
                'country_ids': country_ids,
                'state_id': student_id.sudo().state_id,
                'state_ids': state_ids,
                'marital_status': student_id.maritual_status,
                'mother_tongue_ids': mother_tongue_ids,
                'mother_tongue_id': student_id.sudo().mother_tongue,
                'income':student_id.sudo().income,
                'general_survey_ids': general_survey_ids,
                'general_survey_id': student_id.sudo().general_survey_id,
                'highest_qualification_ids': highest_qualification_ids,
                'highest_qualification_id': student_id.sudo().highest_qualification_id,
                'references_ids': student_id.sudo().reference_ids,
                'parent_ids': student_id.sudo().parent_id,
                'education_background_ids': student_id.sudo().education_background_id,
                'family_ids': student_id.sudo().family_con_ids,
        }
        return request.render("student_portal.student_portal_profile_template", values)

    # Student Profile Update
    @http.route(['/student/profile/update'], type='http', auth="public", website=True, csrf=False)
    def student_profile_update(self, **post):
        partner = request.env.user.partner_id
        student_id = request.env['student.student'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
        vals = {
                'name': post.get('first_name',False) or '',
                'gender': post.get('gender',False),
                'street':post.get('address1',False),
                'street2':post.get('address2',False),
                'state_id':post.get('state_ids',False) and int(post.get('state_ids',False)),
                'zip':post.get('zip',False),
                'country_id':post.get('country_ids',False) and int(post.get('country_ids',False)),
                'phone':post.get('phone',False),
                'mobile':post.get('mobile',False),
                'email':post.get('email',False),
                'contact_phone1':post.get('phone_no',False),
                'contact_mobile1':post.get('mobile_no',False),
                'nric':post.get('nric',False),
                'maritual_status': post.get('marital_status',False),
                'hp_no':post.get('hp_no',False),
                'occupation': post.get('occupation',False),
                'income': '' if post.get('income',False) == 'select_income' else post.get('income',False) ,
                'citizenship': post.get('citizenship',False),
                'remark': post.get('qualification_remark',False),
                'mother_tongue': post.get('mother_tongue_ids',False) and int(post.get('mother_tongue_ids',False)),
                }
        if student_id:
            student_id.sudo().write(vals)
        return request.redirect("/student/portal/profile")