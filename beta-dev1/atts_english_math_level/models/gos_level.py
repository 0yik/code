# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
import logging
from datetime import datetime
import time
from datetime import date
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class Level(models.Model):
    ''' Defining a level class '''
    _name = 'level.level'
    _description = 'Students Level Information'
    
    name = fields.Char('Level Name')
    code = fields.Char('Level Code')
    subject = fields.Selection([('math','Math'),('english','English')],'Subject')
    teacher_id = fields.Many2one('hr.employee',string='Subject Teacher')
    no_levels = fields.Char('Number Of Levels')
    passing_score = fields.Char('Passing Score')
    min_student = fields.Char('Min Number Of Students ')
    max_student = fields.Char('Max Number Of Students ')
    student_ids = fields.One2many('level.student.list','level_id',string='Student List')
    level_ids = fields.One2many('level.list','level_id',string='Level List')
    start_date = fields.Date('Start Date',
                             help='Starting date of Level')
    end_date = fields.Date('End Date',
                            help='Ending of level')
    
    @api.onchange('no_levels')
    def on_change_no_levels(self):
        value=[]
        count = 0
        if self.no_levels and self.name:
            while count<int(self.no_levels):
                count = count+1
                code=re.sub('[^A-Z]', '', self.name)
                value.append({'name': self.name + ' ' + str(count),'code':code + ' ' +str(count),'level_no':count})
            values = {
                'level_ids': value,
                }
            self.update(values) 

class LevelList(models.Model):
    ''' Defining a level list class '''
    _name = 'level.list'
    _description = 'Students Level List Information'
    
    
    code = fields.Char('Level Code')
    name = fields.Char('Level Name')
    teacher_id = fields.Many2one('hr.employee',string='Subject Teacher')
    start_date = fields.Date('Start Date', required=True,
                             help='Starting date of Level')
    end_date = fields.Date('End Date',
                            help='Ending of level')
    level_id = fields.Many2one('level.level',string='Level')
    level_no = fields.Char('Level No')
    
    @api.model
    def create(self, vals):
        '''Method to create level level list and update staff profile'''
        res = super(LevelList, self).create(vals)
        level_name = res.level_id.name
        staff_id = res.teacher_id.id
        date_from = res.start_date
        date_end = res.end_date
        no_levels = res.level_no
        if date_end==False:
            self._cr.execute("insert into staff_level_history (level_name,no_levels,start_date,staff_id) values(%s,%s,%s,%s)",
                             (level_name,no_levels,date_from,staff_id))
        else:
            self._cr.execute("insert into staff_level_history (level_name,no_levels,start_date,end_date,staff_id) values(%s,%s,%s,%s,%s)",
                             (level_name,no_levels,date_from,date_end,staff_id))
        return res
    
    @api.model
    def write(self, vals):
        '''Method to write level level list and update staff profile'''
        res = super(LevelList, self).write(vals)
        if vals.get('teacher_id'):
            for rec in self:
                level_name = rec.level_id.name
                staff_id = vals.get('teacher_id')
                print"staff_id"
                no_levels = rec.level_no
                date_from = rec.start_date
                date_end = rec.end_date
                if date_end==False:
                    self._cr.execute("insert into staff_level_history (level_name,no_levels,start_date,staff_id) values(%s,%s,%s,%s)",
                                 (level_name,no_levels,date_from,staff_id))
                else:
                    self._cr.execute("insert into staff_level_history (level_name,no_levels,start_date,end_date,staff_id) values(%s,%s,%s,%s,%s)",
                                 (level_name,no_levels,date_from,date_end,staff_id))
        return res

    
class LevelStudentList(models.Model):
    ''' Defining a student List for Level'''
    _name = 'level.student.list'
    _description = 'Student List For Level'
    
    level_id = fields.Many2one('level.level',string='Level')
    student_id = fields.Many2one('student.student',string='Student')
    
    @api.model
    def create(self, vals):
        '''Method to create level student list and update student profile'''
        res = super(LevelStudentList, self).create(vals)
        level_name = res.level_id.name
        student_id = res.student_id.id
        no_levels = res.level_id.no_levels
#         teacher_id  = res.level_id.teacher_id.id
        subject = res.level_id.subject
        level = res.level_id.level_ids[0]
        date_from = level.start_date
        date_end = level.end_date
        teacher_id = level.teacher_id.id
        if subject == 'math':
            self._cr.execute("insert into math_level_history (level_name,student_id,teacher_id,math_level_number,start_date) values(%s,%s,%s,'1',%s)",
                         (level_name,student_id,teacher_id,date_from,))
        if subject == 'english':
            self._cr.execute("insert into english_level_history (level_name,student_id,teacher_id,english_level_number,start_date) values(%s,%s,%s,'1',%s)",
                         (level_name,student_id,teacher_id,date_from,))
        return res
    
class MathLevelHistory(models.Model):
    ''' Inherit student Math Level History '''
    _inherit = "math.level.history"
    
    @api.multi
    def write(self, vals):
        '''Write method of Math Level History'''
        res = super(MathLevelHistory, self).write(vals)
        score=0
        if vals.get('math_score'):
            score = vals.get('math_score')
            for rec in self:
                name=rec.level_name
                level_no=str(int(rec.math_level_number)+1)
                level=self.env['level.level'].search([('name','=',name)])
                level_list=self.env['level.list'].search([('name','=',name + ' ' + level_no)])
                date_from = date.today().strftime('%Y-%m-%d')
                if int(score)>=int(level.passing_score) and int(level.no_levels)>=int(level_no):
                    math_level_history = self.env['math.level.history'].search([('student_id','=',rec.student_id.id),('end_date','=',False)], limit=1)
                    self._cr.execute("update math_level_history set end_date=%s where id=%s",(date_from,math_level_history.id))
                    self._cr.execute("insert into math_level_history (level_name,student_id,math_level_number,teacher_id,start_date) values(%s,%s,%s,%s,%s)",
                         (name,rec.student_id.id,level_no,level_list.teacher_id.id,date_from,))
        return res
    
class EnglishLevelHistory(models.Model):
    ''' Inherit student English Level History '''
    _inherit = "english.level.history"
    
    @api.multi
    def write(self, vals):
        '''Write method of English Level History'''
        res = super(EnglishLevelHistory, self).write(vals)
        score=0
        if vals.get('english_score'):
            score = vals.get('english_score')
            for rec in self:
               name=rec.level_name
               level_no=str(int(rec.english_level_number)+1)
               level=self.env['level.level'].search([('name','=',name)])
               level_list=self.env['level.list'].search([('name','=',name + ' ' + level_no)])
               date_from = date.today().strftime('%Y-%m-%d')
               if int(score)>=int(level.passing_score) and int(level.no_levels)>=int(level_no):
                   english_level_history = self.env['english.level.history'].search([('student_id','=',rec.student_id.id),('end_date','=',False)], limit=1)
                   self._cr.execute("update english_level_history set end_date=%s where id=%s",(date_from,english_level_history.id))
                   self._cr.execute("insert into english_level_history (level_name,student_id,english_level_number,teacher_id,start_date) values(%s,%s,%s,%s,%s)",
                         (name,rec.student_id.id,level_no,level_list.teacher_id.id,date_from,))
        return res
