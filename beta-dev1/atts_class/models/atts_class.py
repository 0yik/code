# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import datetime
import time
from datetime import date, datetime
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class Class(models.Model):
    ''' Defining a students class '''
    _name = 'class.class'
    _description = 'Students Class Information'
    
    course_id = fields.Many2one('subject.subject', 'Course Code')
    course_title = fields.Char('Course Title')
    location = fields.Char('Location')
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')

    student_ids = fields.One2many('class.student.list','class_id',string='Student List')
    session_ids = fields.One2many('class.sesion.list','class_id',string='Session List')


    @api.onchange('course_id')
    def onchange_course_id(self):
        for cls in self:
            cls.course_title = cls.course_id.name

    @api.multi
    @api.depends('course_id')
    def name_get(self):
        result = []
        start_year = start_month =start_day = ''
        for class_id in self:
            name = class_id.course_id.name or ''
            if class_id.date_start:
                if class_id.date_start:
                    date_start = datetime.strptime(class_id.date_start, tools.DEFAULT_SERVER_DATE_FORMAT)
                    start_year = date_start.strftime('%Y')
                    start_month = date_start.strftime('%m')
                    start_day = date_start.strftime('%d')
                if class_id.date_end:
                    date_end = datetime.strptime(class_id.date_end, tools.DEFAULT_SERVER_DATE_FORMAT)
                    if start_year != date_end.strftime('%Y'):
                        start_year += '-' + date_end.strftime('%Y')
                    if start_month != date_end.strftime('%m'):
                        start_month += '-' + date_end.strftime('%m')
                    if start_day != date_end.strftime('%d'):
                        start_day += '-' + date_end.strftime('%d')
                name += ' ' + start_year + start_month + start_day
            result.append((class_id.id, "%s" % (name)))
        return result

class RoomRoom(models.Model):
    ''' Defining a room class '''
    _name = 'room.room'
    _description = 'Room Class Information'
    
    name = fields.Char('Name', required=True)


class ClassInstructor(models.Model):
    _name = 'class.instructor'
    _description = 'Class Instructor'
    
    name = fields.Char('Name', required=True)


class ClassSesionList(models.Model):
    _name = 'class.sesion.list'
    _description = 'Class Session List'
    
    class_id = fields.Many2one('class.class',string='Class')
    session_no = fields.Char('Session No')
    date = fields.Date('Date')
    time_start = fields.Float('Time Start')
    time_end = fields.Float('Time End')
    instructor1 = fields.Many2one('class.instructor', 'instructor 1')
    instructor2 = fields.Many2one('class.instructor', 'instructor 2')
    instructor3 = fields.Many2one('class.instructor', 'instructor 3')
    instructor4 = fields.Many2one('class.instructor', 'instructor 4')
    location = fields.Char('Location')
    
    
class ClassStudentList(models.Model):
    ''' Defining a student List for class'''
    _name = 'class.student.list'
    _description = 'Student List For Class'

    @api.onchange('awarded_date')
    def get_date_of_expiry(self):
        for lst in self:
            if lst.class_id.course_id.cert_expiry_period and lst.awarded_date:
                lst.date_of_expiry = fields.Datetime.from_string(lst.awarded_date) + datetime.timedelta(days=(lst.class_id.course_id.cert_expiry_period*365))
        return
    
    class_id = fields.Many2one('class.class', string='Class')
    student_id = fields.Many2one('student.student', string='Student')

    student_name = fields.Char('Student Name')
    attended = fields.Boolean('Attended', default=True)
    module1 = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Module 1')
    module2 = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Module 2')
    module3 = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Module 3')
    module4 = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Module 4')
    module5 = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Module 5')
    module6 = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], 'Module 6')
    module1_comment = fields.Char('Module 1 Comments')
    module2_comment = fields.Char('Module 2 Comments')
    module3_comment = fields.Char('Module 3 Comments')
    module4_comment = fields.Char('Module 4 Comments')
    module5_comment = fields.Char('Module 5 Comments')
    module6_comment = fields.Char('Module 6 Comments')
    training_date = fields.Date('Training Date')
    completion_date = fields.Date('Completion Date')
    certification_no = fields.Char('Certification No.')
    certification_course = fields.Many2one('certification.course', 'JTL No/IADC No/ATTS CERT')
    certified = fields.Boolean('Certified')
    remarks = fields.Char('Remarks')
    awarded_date = fields.Date('Date Awarded')
    certification_received_printed_date = fields.Date('Certificate Received/Printed Date')
    certification_sent_out_date = fields.Date('Certificate Sent Out Date')
    retention_period = fields.Char('Retention Period')
    date_of_expiry = fields.Date('Date of Expiry', default=get_date_of_expiry)
    file_name = fields.Char('File Name',)
    file = fields.Binary('File')

    @api.onchange('student_id')
    def onchange_student_id(self):
        for lst in self:
            if not lst.student_name:
                lst.student_name = lst.student_id.name

    @api.onchange('attended')
    def onchange_attended(self):
        for lst in self:
            lst.certified = lst.attended

class CertificationCourse(models.Model):
    _name = 'certification.course'

    name = fields.Char('Certification Course Name')

class StudentStudent(models.Model):
    ''' Defining a student information '''
    _inherit = 'student.student'
    _description = 'Student Information'
    
    
    @api.multi
    def set_alumni(self):
        '''Method to change state to alumni'''
        for rec in self:
            rec.state = 'alumni'
            class_id = self.env['class.student.list'].search([('student_id','=',rec.id)])
            date_end = date.today().strftime('%Y-%m-%d')
            self._cr.execute("delete from class_student_list where student_id=%s",(rec.id,))
            class_history = self.env['class.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
            if class_history:
                self._cr.execute("update class_history set end_date=%s where id=%s",(date_end,class_history.id))
            for cca_id in self.env['student.list.cca'].search([('student_id','=',rec.id)]):
                self._cr.execute("delete from student_list_cca where student_id=%s",(rec.id,))
            for vocational_id in self.env['student.list'].search([('student_id','=',rec.id)]):
                self._cr.execute("delete from student_list where student_id=%s",(rec.id,))
            
            for level_id in self.env['level.student.list'].search([('student_id','=',rec.id)]):
                level_subject=level_id.level_id.subject
                self._cr.execute("delete from level_student_list where student_id=%s",(rec.id,))
                if level_subject=='english':
                    english_level_history = self.env['english.level.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                    if english_level_history:
                        self._cr.execute("update english_level_history set end_date=%s where id=%s",(date_end,english_level_history.id))
                if level_subject=='math':
                    math_level_history = self.env['math.level.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                    if math_level_history:
                        self._cr.execute("update math_level_history set end_date=%s where id=%s",(date_end,math_level_history.id))
            
        return True
    
    @api.multi
    def write(self, vals):
        '''Write method of Student'''
        res = super(StudentStudent, self).write(vals)
        for rec in self:
            if vals.get('withdraw_date'):
                class_id = self.env['class.student.list'].search([('student_id','=',rec.id)])
                date_end = date.today().strftime('%Y-%m-%d')
                self._cr.execute("delete from class_student_list where student_id=%s",(rec.id,))
                class_history = self.env['class.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                if class_history:
                    self._cr.execute("update class_history set end_date=%s where id=%s",(date_end,class_history.id))
                for cca_id in self.env['student.list.cca'].search([('student_id','=',rec.id)]):
                    self._cr.execute("delete from student_list_cca where student_id=%s",(rec.id,))
                for vocational_id in self.env['student.list'].search([('student_id','=',rec.id)]):
                    self._cr.execute("delete from student_list where student_id=%s",(rec.id,))
                for level_id in self.env['level.student.list'].search([('student_id','=',rec.id)]):
                    level_subject=level_id.level_id.subject
                    self._cr.execute("delete from level_student_list where student_id=%s",(rec.id,))
                    if level_subject=='english':
                        english_level_history = self.env['english.level.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                        if english_level_history:
                            self._cr.execute("update english_level_history set end_date=%s where id=%s",(date_end,english_level_history.id))
                    if level_subject=='math':
                        math_level_history = self.env['math.level.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                        if math_level_history:
                            self._cr.execute("update math_level_history set end_date=%s where id=%s",(date_end,math_level_history.id))
            if vals.get('de_registration'):
                class_id = self.env['class.student.list'].search([('student_id','=',rec.id)])
                date_end = date.today().strftime('%Y-%m-%d')
                self._cr.execute("delete from class_student_list where student_id=%s",(rec.id,))
                class_history = self.env['class.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                if class_history:
                    self._cr.execute("update class_history set end_date=%s where id=%s",(date_end,class_history.id))
                
                for cca_id in self.env['student.list.cca'].search([('student_id','=',rec.id)]):
                    self._cr.execute("delete from student_list_cca where student_id=%s",(rec.id,))
                for vocational_id in self.env['student.list'].search([('student_id','=',rec.id)]):
                    self._cr.execute("delete from student_list where student_id=%s",(rec.id,))
                for level_id in self.env['level.student.list'].search([('student_id','=',rec.id)]):
                    level_subject=level_id.level_id.subject
                    self._cr.execute("delete from level_student_list where student_id=%s",(rec.id,))
                    if level_subject=='english':
                        english_level_history = self.env['english.level.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                        if english_level_history:
                            self._cr.execute("update english_level_history set end_date=%s where id=%s",(date_end,english_level_history.id))
                    if level_subject=='math':
                        math_level_history = self.env['math.level.history'].search([('student_id','=',rec.id),('end_date','=',False)], limit=1)
                        if math_level_history:
                            self._cr.execute("update math_level_history set end_date=%s where id=%s",(date_end,math_level_history.id))
#             if vals.get('programme'):
#                 programme=vals.get('programme')
#                 age = self.age
#                 if programme=='ASD' and (age>=7 and age<=12):
#                     for class_id in self.env['class.class'].search([('class_level','=','love'),('session','=','pm')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme=='ASD' and (age>=13 and age<=18):
#                     for class_id in self.env['class.class'].search([('class_level','=','love'),('session','=','am')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme in ['MID','Integrated'] and (age>=7 and age<=8):
#                     for class_id in self.env['class.class'].search([('class_level','=','joy')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme in ['MID','Integrated'] and (age>=9 and age<=10):
#                     for class_id in self.env['class.class'].search([('class_level','=','peace')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme in ['MID','Integrated'] and (age>=11 and age<=12):
#                     for class_id in self.env['class.class'].search([('class_level','=','hope')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme in ['MID','Integrated'] and (age>=13 and age<=14):
#                     for class_id in self.env['class.class'].search([('class_level','=','kindness')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme in ['MID','Integrated'] and (age>=15 and age<=16):
#                     for class_id in self.env['class.class'].search([('class_level','=','victory')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                 if programme in ['MID','Integrated'] and (age>=17 and age<=18):
#                     for class_id in self.env['class.class'].search([('class_level','=','glory')], limit=1, order='no_records ASC'):
#                         records_id=class_id.id
#                         value = {
#                                  'class_id':records_id,
#                                  'student_id' : rec.id,
#                                  }
#                         self.env['class.student.list'].create(value)
#                     
            
        return res   

    
