# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime
import time
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError,UserError
from odoo.modules.module import get_module_resource
from openerp import http

_logger = logging.getLogger(__name__)

class StudentCCA(models.Model):
    ''' Defining a student CCA session information '''
    _name = 'student.cca'
    _description = 'Student CCA session Information'
    
    name = fields.Char('CCA Name')
    code = fields.Char('Code')
    session = fields.Selection([('AM','AM'),('PM','PM'),('Others','Others')],'Session')
    comment = fields.Text('Comment')
    class_id = fields.Many2one('class.class',string='Class')
    teacher_id = fields.Many2many('hr.employee',string='Teacher')
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    student_ids = fields.One2many('student.list.cca','cca_id',string='Student List')
    
    @api.onchange('class_id')
    def on_change_class(self):
        value=[]
        if self.class_id:
            student_list= self.env['class.student.list']    
            student_ids = student_list.search([('class_id', '=', self.class_id.id)])
            for student in student_ids:
                value.append({'student_id': student.student_id.id})
            values = {
                'student_ids': value,
                }
            self.update(values)
    @api.model
    def create(self,vals):
        res = super(StudentCCA, self).create(vals)
        if len(res.teacher_id) > 5:
            raise UserError(
                _('CCA can not select more then 5 teacher.'))
        return res

    @api.multi
    def write(self, vals):
        res = super(StudentCCA, self).write(vals)
        for record in self:
            if len(record.teacher_id) > 5:
                raise UserError(
                    _('CCA can not select more then 5 teacher.'))
        return res

    
class StudentListCCA(models.Model):
    ''' Defining a student List for CCA '''
    _name = 'student.list.cca'
    _description = 'Student List For CCA'
    
    cca_id = fields.Many2one('student.cca',string='CCA')
    student_id = fields.Many2one('student.student',string='Student')