# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api

class houseColour(models.Model):
    _name = 'house.colour'
    _description = 'Describes about house color'
    
    name = fields.Char('House Colour')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    #veducation_id = fields.Many2one('vocational.education',string='Class Code')
    class_line = fields.One2many('class.line','house_color_id',string='Class Code')
    student_line = fields.One2many('student.line','house_color_id',string='Student List')
    employee_line = fields.One2many('hr.employee.line','house_color_id',string='Staff List')
    
    @api.onchange('class_line')
    def class_change(self):
        vals ={}
        lst=[]
        list_std=[]
        active_id=self.env.context.get('active_id')
        vals['house_color_id'] = active_id or self._origin.id or self.id
        for student_id in self.student_line:
            list_std.append(student_id.student_id.id)
        if self.class_line:
            for line in self.class_line:
                class_id=line.class_id
                if class_id:
                    student_ids=class_id.student_ids
                    if student_ids:
                        for student_id in student_ids:
                            lst.append(student_id.student_id.id)
        return {'value': {'student_line':[(0, 0, {'student_id':student_id}) for student_id in lst]}}
                   
    
    
class StudentList(models.Model):
    ''' Defining a student List for House Color '''
    _name = 'student.line'
    _description = 'Student List For House Color'
    
    house_color_id = fields.Many2one('house.colour',string='House Color')
    student_id = fields.Many2one('student.student',string='Student')
    
    
class ClassLine(models.Model):
    ''' Defining a Class List for House Color '''
    _name = 'class.line'
    _description = 'Class List For House Color'
    
    class_id = fields.Many2one('class.class',string='Class Code')
    house_color_id = fields.Many2one('house.colour',string='House Color')
    
class staff_line(models.Model):
    ''' Defining a Class List for Staff '''
    _name = 'hr.employee.line'
    _description = 'Defining a Class List for Staff'
    
    employee_id = fields.Many2one('hr.employee',string='Staff')
    house_color_id = fields.Many2one('house.colour',string='House Color')
    



