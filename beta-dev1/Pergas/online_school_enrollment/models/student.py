# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EducationBackground(models.Model):
    _name = 'education.background'

    institution = fields.Char('Institution')
    achievement = fields.Text('Achievement')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    student_id = fields.Many2one('sstudent.student', 'Student')

class HighestQualification(models.Model):
	_name = 'highest.qualification'

	name = fields.Char('Name')

	_sql_constraints = [
        ('code_name_uniq', 'unique (name)', 'The name must be unique!')
    ]

class GeneralSurvey(models.Model):
	_name = 'general.survey'

	name = fields.Char('Name')

	_sql_constraints = [
        ('code_name_uniq', 'unique (name)', 'The name must be unique!')
    ]	

class StudentStudent(models.Model):
    ''' Defining a student information '''
    _inherit = 'student.student'

    citizenship = fields.Char('Citizenship')
    nric = fields.Char('NRIC')
    hp_no = fields.Char('Hp No.')
    occupation = fields.Char('Occupation')
    income = fields.Selection([
    	('less_then_1500', 'Less 1500'),
        ('1500_2000', '1500-2000'),
        ('2001_3000', '2001-3000'),
        ('3001_above', '3001 Above'),
        ],string='Income', default='less_then_1500')
    highest_qualification_id = fields.Many2one('highest.qualification', 'Highest Qualification')
    general_survey_id = fields.Many2one('general.survey', 'General Survey')
    education_background_id = fields.One2many('education.background', 'student_id', String='General Survey')