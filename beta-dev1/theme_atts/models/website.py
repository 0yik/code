# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import api, fields, models, tools, _

class WebsiteATTS(models.Model):
    _inherit = "website"

    def get_courses_level(self, is_popular=None):
        return self.env['course.level'].sudo().search([])

    def get_courses(self, is_popular=None):
        domain = []
        limit = None
        if is_popular:
            limit = 3
            domain = [('is_popular', '=', is_popular)]
        else:
            domain = [('id', 'in', [cls.course_id.id for cls in self.get_course_class()])]
        return self.env['subject.subject'].sudo().search(domain, limit=limit)

    def get_indusreys(self):
        return self.env['course.industry'].sudo().search([])

    def get_course_class(self, course=None):
        search_course = [('date_start', '>=', fields.Date.today())]
        if course:
            search_course += [('course_id', '=', course.id)]
        return self.env['class.class'].sudo().search(search_course)

    def get_registration_files(self):
        registration_files_obj = self.env['registration.files'].sudo()
        registration_files_corporate = registration_files_obj.search([('student_type', '=', 'corporate')], order="id desc", limit=1)
        registration_files_individual = registration_files_obj.search([('student_type', '=', 'individual')], order="id desc", limit=1)
        return registration_files_corporate + registration_files_individual

    def get_footer_courses(self):
        return self.env['subject.subject'].sudo().search([('is_footer', '=', True)])

class RegistrationFiles(models.Model):
    _name = "registration.files"
    _rec_name = "filename"

    student_type = fields.Selection([('corporate', 'Corporate'), ('individual', 'Individual')], string="Student Type", default="individual")
    registration_file = fields.Binary(string='Registration File', required=True)
    filename = fields.Char()
