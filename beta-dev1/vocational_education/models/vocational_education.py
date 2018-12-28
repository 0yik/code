# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime
import time
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from openerp import http

_logger = logging.getLogger(__name__)

class VocationalEducation(models.Model):
    ''' Defining a student vocational education information '''
    _name = 'vocational.education'
    _description = 'Student Vocational Education Information'
    
    name = fields.Char('Programme Name')
    description = fields.Text('Vocational Education Description')
    level = fields.Selection([('Rotation','Rotation'),('Specialization','Specialization')],'Level')
    teacher_id = fields.Many2one('hr.employee',string='Teacher')
    student_ids = fields.One2many('student.list','veducation_id',string='Student List')
    

    
class StudentList(models.Model):
    ''' Defining a student List for vocational education '''
    _name = 'student.list'
    _description = 'Student List For Vocational Education'
    
    veducation_id = fields.Many2one('vocational.education',string='Vocational Education')
    student_id = fields.Many2one('student.student',string='Student')
    
