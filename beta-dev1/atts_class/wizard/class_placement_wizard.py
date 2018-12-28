# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import time
from datetime import date
from dateutil import relativedelta

from odoo import api, fields, models


class ClassPlacementWizard(models.TransientModel):
    _name = 'class.placement.wizard'
    _description = 'Class Placement Wizard'

    
    @api.multi
    def run_placement(self):
        
        self._cr.execute("delete from class_student_list")
        date_end = date.today().strftime('%Y-%m-%d')
        for class_data in self.env['class.class'].search([]):
            self._cr.execute("update class_class set start_date=%s where id=%s",(date_end,class_data.id))
        for class_history in self.env['class.history'].search([('end_date','=',False)]):
            self._cr.execute("update class_history set end_date=%s where id=%s",(date_end,class_history.id))
        for student in self.env['student.student'].search([('state','=','done')]):
            age = student.age
            if student.programme=='ASD' and (age>=7 and age<=12):
                for class_id in self.env['class.class'].search([('class_level','=','love'),('session','=','pm')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
            if student.programme=='ASD' and (age>=13 and age<=18):
                    for class_id in self.env['class.class'].search([('class_level','=','love'),('session','=','am')], limit=1, order='no_records ASC'):
                        records_id=class_id.id
                        value = {
                                 'class_id':records_id,
                                 'student_id' : student.id,
                                 }
                        self.env['class.student.list'].create(value)
            if student.programme in ['MID','Integrated'] and (age>=7 and age<=8):
                for class_id in self.env['class.class'].search([('class_level','=','joy')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
            if student.programme in ['MID','Integrated'] and (age>=9 and age<=10):
                for class_id in self.env['class.class'].search([('class_level','=','peace')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
            if student.programme in ['MID','Integrated'] and (age>=11 and age<=12):
                for class_id in self.env['class.class'].search([('class_level','=','hope')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
            if student.programme in ['MID','Integrated'] and (age>=13 and age<=14):
                for class_id in self.env['class.class'].search([('class_level','=','kindness')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
            if student.programme in ['MID','Integrated'] and (age>=15 and age<=16):
                for class_id in self.env['class.class'].search([('class_level','=','victory')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
            if student.programme in ['MID','Integrated'] and (age>=17 and age<=18):
                for class_id in self.env['class.class'].search([('class_level','=','glory')], limit=1, order='no_records ASC'):
                    records_id=class_id.id
                    value = {
                             'class_id':records_id,
                             'student_id' : student.id,
                             }
                    self.env['class.student.list'].create(value)
    
        return True