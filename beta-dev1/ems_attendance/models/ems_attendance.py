# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError

class DailyAttendance(models.Model):
    _inherit = 'daily.attendance'
    
    @api.onchange('class_id')
    def _onchange_class_id(self):
        values = {
            'subject_id': self.class_id.subject_id.id,
            'academic_year_id': self.class_id.intake_id.id,
            'date': self.class_id.start_time,
            'teacher_id': self.class_id.teacher_id.id,
            'classroom_id': self.class_id.classroom_id.id,
        }
        self.update(values)
    
    subject_id = fields.Many2one('subject.subject','Subject')
    class_id = fields.Many2one('ems.class','Class')
    date = fields.Datetime('Date')
    academic_year_id = fields.Many2one('academic.year','Intake')
    teacher_id = fields.Many2one('hr.employee','Teacher')
    classroom_id = fields.Many2one('ems.classroom','Classroom')
    
    
    @api.multi
    def attendance_validate(self):
        '''Method to validate attendance'''
        sheet_line_obj = self.env['attendance.sheet.line']
        acadmic_year_obj = self.env['academic.year']
        acadmic_month_obj = self.env['academic.month']
        attendance_sheet_obj = self.env['attendance.sheet']

        for line in self:
            date = datetime.strptime(line.date, "%Y-%m-%d %H:%M:%S")
            year = date.year
            year_ids = line.academic_year_id
            month_ids = acadmic_month_obj.search([('date_start', '<=', date),
                                                  ('date_stop', '>=', date),
                                                  ('year_id', 'in',
                                                   year_ids.ids)])
            if month_ids:
                month_data = month_ids
                domain = [('month_id', 'in', month_ids.ids),
                          ('year_id', 'in', year_ids.ids)]
                att_sheet_ids = attendance_sheet_obj.search(domain)
                attendance_sheet_id = (att_sheet_ids and att_sheet_ids[0] or
                                       False)
                if not attendance_sheet_id:
                    sheet = {'name':  month_data.name + '-' + str(year),
                             'standard_id': line.standard_id.id,
                             'user_id': line.user_id.id,
                             'month_id': month_data.id,
                             'year_id': year_ids and year_ids.id or False}
                    attendance_sheet_id = attendance_sheet_obj.create(sheet)
                    for student_id in line.student_ids:
                        line_dict = {'roll_no': student_id.roll_no,
                                     'standard_id': attendance_sheet_id.id,
                                     'name': student_id.stud_id.student_name}
                        sheet_line_obj.create(line_dict)
                        for student_id in line.student_ids:
                            sheet_line_obj.read([student_id.roll_no])
                            domain = [('roll_no', '=', student_id.roll_no)]
                            search_id = sheet_line_obj.search(domain)
                            # compute attendance of each day
                            if date.day == 1 and student_id.is_absent:
                                val = {'one': False}

                            elif date.day == 1 and not student_id.is_absent:
                                val = {'one': True}

                            elif date.day == 2 and student_id.is_absent:
                                val = {'two': False}

                            elif date.day == 2 and not student_id.is_absent:
                                val = {'two': True}

                            elif date.day == 3 and student_id.is_absent:
                                val = {'three': False}

                            elif date.day == 3 and not student_id.is_absent:
                                val = {'three': True}

                            elif date.day == 4 and student_id.is_absent:
                                val = {'four': False}

                            elif date.day == 4 and not student_id.is_absent:
                                val = {'four': True}

                            elif date.day == 5 and student_id.is_absent:
                                val = {'five': False}

                            elif date.day == 5 and not student_id.is_absent:
                                val = {'five': True}

                            elif date.day == 6 and student_id.is_absent:
                                val = {'six': False}

                            elif date.day == 6 and not student_id.is_absent:
                                val = {'six': True}

                            elif date.day == 7 and student_id.is_absent:
                                val = {'seven': False}

                            elif date.day == 7 and not student_id.is_absent:
                                val = {'seven': True}

                            elif date.day == 8 and student_id.is_absent:
                                val = {'eight': False}

                            elif date.day == 8 and not student_id.is_absent:
                                val = {'eight': True}

                            elif date.day == 9 and student_id.is_absent:
                                val = {'nine': False}

                            elif date.day == 9 and not student_id.is_absent:
                                val = {'nine': True}

                            elif date.day == 10 and student_id.is_absent:
                                val = {'ten': False}

                            elif date.day == 10 and not student_id.is_absent:
                                val = {'ten': True}

                            elif date.day == 11 and student_id.is_absent:
                                val = {'one_1': False}

                            elif date.day == 11 and not student_id.is_absent:
                                val = {'one_1': True}

                            elif date.day == 12 and student_id.is_absent:
                                val = {'one_2': False}

                            elif date.day == 12 and not student_id.is_absent:
                                val = {'one_2': True}

                            elif date.day == 13 and student_id.is_absent:
                                val = {'one_3': False}

                            elif date.day == 13 and not student_id.is_absent:
                                val = {'one_3': True}

                            elif date.day == 14 and student_id.is_absent:
                                val = {'one_4': False}

                            elif date.day == 14 and not student_id.is_absent:
                                val = {'one_4': True}

                            elif date.day == 15 and student_id.is_absent:
                                val = {'one_5': False}

                            elif date.day == 15 and not student_id.is_absent:
                                val = {'one_5': True}

                            elif date.day == 16 and student_id.is_absent:
                                val = {'one_6': False}

                            elif date.day == 16 and not student_id.is_absent:
                                val = {'one_6': True}

                            elif date.day == 17 and student_id.is_absent:
                                val = {'one_7': False}

                            elif date.day == 17 and not student_id.is_absent:
                                val = {'one_7': True}

                            elif date.day == 18 and student_id.is_absent:
                                val = {'one_8': False}

                            elif date.day == 18 and not student_id.is_absent:
                                val = {'one_8': True}

                            elif date.day == 19 and student_id.is_absent:
                                val = {'one_9': False}

                            elif date.day == 19 and not student_id.is_absent:
                                val = {'one_9': True}

                            elif date.day == 20 and student_id.is_absent:
                                val = {'one_0': False}

                            elif date.day == 20 and not student_id.is_absent:
                                val = {'one_0': True}

                            elif date.day == 21 and student_id.is_absent:
                                val = {'two_1': False}

                            elif date.day == 21 and not student_id.is_absent:
                                val = {'two_1': True}

                            elif date.day == 22 and student_id.is_absent:
                                val = {'two_2': False}

                            elif date.day == 22 and not student_id.is_absent:
                                val = {'two_2': True}

                            elif date.day == 23 and student_id.is_absent:
                                val = {'two_3': False}

                            elif date.day == 23 and not student_id.is_absent:
                                val = {'two_3': True}

                            elif date.day == 24 and student_id.is_absent:
                                val = {'two_4': False}

                            elif date.day == 24 and not student_id.is_absent:
                                val = {'two_4': True}

                            elif date.day == 25 and student_id.is_absent:
                                val = {'two_5': False}

                            elif date.day == 25 and not student_id.is_absent:
                                val = {'two_5': True}

                            elif date.day == 26 and student_id.is_absent:
                                val = {'two_6': False}

                            elif date.day == 26 and not student_id.is_absent:
                                val = {'two_6': True}

                            elif date.day == 27 and student_id.is_absent:
                                val = {'two_7': False}

                            elif date.day == 27 and not student_id.is_absent:
                                val = {'two_7': True}

                            elif date.day == 28 and student_id.is_absent:
                                val = {'two_8': False}

                            elif date.day == 28 and not student_id.is_absent:
                                val = {'two_8': True}

                            elif date.day == 29 and student_id.is_absent:
                                val = {'two_9': False}

                            elif date.day == 29 and not student_id.is_absent:
                                val = {'two_9': True}

                            elif date.day == 30 and student_id.is_absent:
                                val = {'two_0': False}

                            elif date.day == 30 and not student_id.is_absent:
                                val = {'two_0': True}

                            elif date.day == 31 and student_id.is_absent:
                                val = {'three_1': False}

                            elif date.day == 31 and not student_id.is_absent:
                                val = {'three_1': True}
                            else:
                                val = {}
                            if search_id:
                                search_id.write(val)

                if attendance_sheet_id:
                    for student_id in line.student_ids:
                        sheet_line_obj.read([student_id.roll_no])
                        domain = [('roll_no', '=', student_id.roll_no),
                                  ('standard_id', '=', attendance_sheet_id.id)]
                        search_id = sheet_line_obj.search(domain)

                        if date.day == 1 and student_id.is_absent:
                            val = {'one': False}

                        elif date.day == 1 and not student_id.is_absent:
                            val = {'one': True}

                        elif date.day == 2 and student_id.is_absent:
                            val = {'two': False}

                        elif date.day == 2 and not student_id.is_absent:
                            val = {'two': True}

                        elif date.day == 3 and student_id.is_absent:
                            val = {'three': False}

                        elif date.day == 3 and not student_id.is_absent:
                            val = {'three': True}

                        elif date.day == 4 and student_id.is_absent:
                            val = {'four': False}

                        elif date.day == 4 and not student_id.is_absent:
                            val = {'four': True}

                        elif date.day == 5 and student_id.is_absent:
                            val = {'five': False}

                        elif date.day == 5 and not student_id.is_absent:
                            val = {'five': True}

                        elif date.day == 6 and student_id.is_absent:
                            val = {'six': False}

                        elif date.day == 6 and not student_id.is_absent:
                            val = {'six': True}

                        elif date.day == 7 and student_id.is_absent:
                            val = {'seven': False}

                        elif date.day == 7 and not student_id.is_absent:
                            val = {'seven': True}

                        elif date.day == 8 and student_id.is_absent:
                            val = {'eight': False}

                        elif date.day == 8 and not student_id.is_absent:
                            val = {'eight': True}

                        elif date.day == 9 and student_id.is_absent:
                            val = {'nine': False}

                        elif date.day == 9 and not student_id.is_absent:
                            val = {'nine': True}

                        elif date.day == 10 and student_id.is_absent:
                            val = {'ten': False}

                        elif date.day == 10 and not student_id.is_absent:
                            val = {'ten': True}

                        elif date.day == 11 and student_id.is_absent:
                            val = {'one_1': False}

                        elif date.day == 11 and not student_id.is_absent:
                            val = {'one_1': True}

                        elif date.day == 12 and student_id.is_absent:
                            val = {'one_2': False}

                        elif date.day == 12 and not student_id.is_absent:
                            val = {'one_2': True}

                        elif date.day == 13 and student_id.is_absent:
                            val = {'one_3': False}

                        elif date.day == 13 and not student_id.is_absent:
                            val = {'one_3': True}

                        elif date.day == 14 and student_id.is_absent:
                            val = {'one_4': False}

                        elif date.day == 14 and not student_id.is_absent:
                            val = {'one_4': True}

                        elif date.day == 15 and student_id.is_absent:
                            val = {'one_5': False}

                        elif date.day == 15 and not student_id.is_absent:
                            val = {'one_5': True}

                        elif date.day == 16 and student_id.is_absent:
                            val = {'one_6': False}

                        elif date.day == 16 and not student_id.is_absent:
                            val = {'one_6': True}

                        elif date.day == 17 and student_id.is_absent:
                            val = {'one_7': False}

                        elif date.day == 17 and not student_id.is_absent:
                            val = {'one_7': True}

                        elif date.day == 18 and student_id.is_absent:
                            val = {'one_8': False}

                        elif date.day == 18 and not student_id.is_absent:
                            val = {'one_8': True}

                        elif date.day == 19 and student_id.is_absent:
                            val = {'one_9': False}

                        elif date.day == 19 and not student_id.is_absent:
                            val = {'one_9': True}

                        elif date.day == 20 and student_id.is_absent:
                            val = {'one_0': False}

                        elif date.day == 20 and not student_id.is_absent:
                            val = {'one_0': True}

                        elif date.day == 21 and student_id.is_absent:
                            val = {'two_1': False}

                        elif date.day == 21 and not student_id.is_absent:
                            val = {'two_1': True}

                        elif date.day == 22 and student_id.is_absent:
                            val = {'two_2': False}

                        elif date.day == 22 and not student_id.is_absent:
                            val = {'two_2': True}

                        elif date.day == 23 and student_id.is_absent:
                            val = {'two_3': False}

                        elif date.day == 23 and not student_id.is_absent:
                            val = {'two_3': True}

                        elif date.day == 24 and student_id.is_absent:
                            val = {'two_4': False}

                        elif date.day == 24 and not student_id.is_absent:
                            val = {'two_4': True}

                        elif date.day == 25 and student_id.is_absent:
                            val = {'two_5': False}

                        elif date.day == 25 and not student_id.is_absent:
                            val = {'two_5': True}

                        elif date.day == 26 and student_id.is_absent:
                            val = {'two_6': False}

                        elif date.day == 26 and not student_id.is_absent:
                            val = {'two_6': True}

                        elif date.day == 27 and student_id.is_absent:
                            val = {'two_7': False}

                        elif date.day == 27 and not student_id.is_absent:
                            val = {'two_7': True}

                        elif date.day == 28 and student_id.is_absent:
                            val = {'two_8': False}

                        elif date.day == 28 and not student_id.is_absent:
                            val = {'two_8': True}

                        elif date.day == 29 and student_id.is_absent:
                            val = {'two_9': False}

                        elif date.day == 29 and not student_id.is_absent:
                            val = {'two_9': True}

                        elif date.day == 30 and student_id.is_absent:
                            val = {'two_0': False}

                        elif date.day == 30 and not student_id.is_absent:
                            val = {'two_0': True}

                        elif date.day == 31 and student_id.is_absent:
                            val = {'three_1': False}

                        elif date.day == 31 and not student_id.is_absent:
                            val = {'three_1': True}
                        else:
                            val = {}
                        if search_id:
                            search_id.write(val)
        self.write({'state': 'validate'})
        return True


class DailyAttendanceLine(models.Model):
    _inherit = 'daily.attendance.line'
    
    @api.one
    @api.depends('is_absent','state')
    def _compute_absent(self):
        if self.state == 'validate':
            if self.is_absent:
                self.total_absent = 1
    
    @api.one
    @api.depends('is_present','state')
    def _compute_present(self):
        if self.state == 'validate':
            if self.is_present:
                self.total_present = 1
    
    @api.one
    @api.depends('is_present','is_absent','state')
    def _compute_total(self):
        if self.state == 'validate':
            self.total_class = 1
    
    @api.one
    @api.depends('stud_id','is_present','is_absent','state')
    def _compute_ratio(self):
        if self.state == 'validate':
            line_ids = self.search([('stud_id','=',self.stud_id.id)])
            total_class = 0
            total_present = 0
            total_absent = 0
            self.absent_ratio = 0
            self.present_ratio = 0
            if line_ids:
                for line in line_ids:
                    total_class += 1
                    if line.is_present:
                        total_present = 1
                    if line.is_absent:
                        total_absent = 1
            if self.is_present:
                self.present_ratio = (total_present * 100)
            if self.is_absent:
                self.absent_ratio = (total_absent * 100)
        
    
    subject_id = fields.Many2one(related='standard_id.subject_id',string="Subject",store=True)
    class_id = fields.Many2one(related='standard_id.class_id',string="Class",store=True)
    academic_year_id = fields.Many2one(related='standard_id.academic_year_id',string="Intake",store=True)
    teacher_id = fields.Many2one(related='standard_id.teacher_id',string="Teacher",store=True)
    state = fields.Selection(related='standard_id.state',string="State",store=True)
    total_absent = fields.Integer(string='Total Absent', store=True, readonly=True, compute='_compute_absent',track_visibility='always')
    total_present = fields.Integer(string='Total Present', store=True, readonly=True, compute='_compute_present',track_visibility='always')
    total_class = fields.Integer(string='Total', store=True, readonly=True, compute='_compute_total',track_visibility='always')
    absent_ratio = fields.Float(string='Absent Ratio', store=True, readonly=True, compute='_compute_ratio',track_visibility='always',group_operator='avg')
    present_ratio = fields.Float(string='Present Ratio', store=True, readonly=True, compute='_compute_ratio',track_visibility='always',group_operator='avg')
    
