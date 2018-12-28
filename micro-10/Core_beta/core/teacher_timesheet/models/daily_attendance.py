# -*- coding: utf-8 -*-
from __future__ import division
import time
from datetime import datetime,timedelta
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError
import math
from dateutil import tz
import pytz

class hr_timesheet_sheet_sheet(models.Model):
    _inherit = 'hr_timesheet_sheet.sheet'
    
    attendance_id = fields.Many2one('daily.attendance','Attendance Sheet')
    attendance_ids = fields.Many2many('daily.attendance', 'timesheet_attendance_rel', 'timesheet_id', 'attendance_id', string='Attendances')
    skip_attendance_ids = fields.Many2many('daily.attendance', 'timesheet_skip_attendance_rel', 'timesheet_id', 'attendance_id', string='Skip Attendances')
    school_id = fields.Many2one('school.school','Branch')
    
    @api.multi
    def action_reset_draft_timesheet(self):
        timesheet_pool = self.env['hr_timesheet_sheet.sheet']
        if self._context.has_key('active_ids'):
            for timesheet_id in self._context.get('active_ids'):
                timesheet_obj = timesheet_pool.browse(timesheet_id)
                timesheet_obj.action_timesheet_draft()
                timesheet_obj.write({'state': 'draft'})
    
    @api.multi
    def action_timesheet_done(self):
        if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            raise UserError(_('Only an HR Officer or Manager can approve timesheets.'))
        if self.filtered(lambda sheet: sheet.state == 'new'):
            raise UserError(_("Cannot approve a non-submitted timesheet."))
        self.write({'state': 'done'})
    
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    class_id = fields.Many2one('ems.class','Class')
    school_id = fields.Many2one('school.school','Branch')

    @api.depends('date', 'user_id', 'project_id', 'account_id', 'sheet_id_computed.date_to',
                 'sheet_id_computed.date_from', 'sheet_id_computed.employee_id')
    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet
        """
        for ts_line in self:
            # TODO: Disable project_id
            # if not ts_line.project_id:
            #     continue
            timeshet_journal = self.env.ref('stable_hr_timesheet_invoice.timesheet_journal')
            if timeshet_journal and timeshet_journal.id:
                if ts_line.journal_id and ts_line.journal_id.id:
                    if ts_line.journal_id.id == timeshet_journal.id:
                        sheets = self.env['hr_timesheet_sheet.sheet'].search(
                            [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
                             ('state', 'in', ['draft', 'new'])])
                        if sheets:
                            # [0] because only one sheet possible for an employee between 2 dates
                            ts_line.sheet_id_computed = sheets[0]
                            ts_line.sheet_id = sheets[0]

class SchoolSchool(models.Model):
    _inherit = 'school.school'
    
    project_id = fields.Many2one('project.project','Project',required=True)

class DailyAttendance(models.Model):
    _inherit = 'daily.attendance'
    
    _rec_name = 'class_id'
    
    
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=False,
                                  help="Select Standard",
                                  states={'validate': [('readonly', True)]})
    project_id = fields.Many2one('project.project','Project')
    school_id = fields.Many2one('school.school','Branch')
    action_draft = fields.Boolean('Draft Action')
    state = fields.Selection([('draft', 'Draft'),('submitted', 'Submitted'),('validate', 'Validate')],
                             'State', readonly=True, default='draft')
    
    
    @api.onchange('class_id')
    def _onchange_class_id(self):
        student_list = []
        
        if self.class_id.student_ids:
            for student in self.class_id.student_ids:
                student_list.append({
                	'roll_no': student.roll_no,
                    'stud_id': student.student_id.id,
                    'is_present': False
                })
        values = {
            'subject_id': self.class_id.subject_id.id,
            'academic_year_id': self.class_id.intake_id.id,
            'date': self.class_id.start_time,
            'teacher_id': self.class_id.teacher_id.id,
            'classroom_id': self.class_id.classroom_id.id,
            'std_id': self.class_id.standard_id.id,
            'school_id': self.class_id.school_id.id,
            'project_id': self.class_id.school_id.project_id.id,
        }
        self.student_ids = student_list
        self.update(values)
    
    
    @api.multi
    def action_draft_attendance_sheet(self):
        attendace_pool = self.env['daily.attendance']
        if self._context.has_key('active_ids'):
            for attendance_id in self._context.get('active_ids'):
                attendace_obj = attendace_pool.browse(attendance_id)
                attendace_obj.write({'state': 'draft', 'action_draft': True})
    
    
    @api.multi
    def action_submit_attendance_sheet(self):
        attendace_pool = self.env['daily.attendance']
        if self._context.has_key('active_ids'):
            for attendance_id in self._context.get('active_ids'):
                attendace_obj = attendace_pool.browse(attendance_id)
                if attendace_obj.action_draft:
                    attendace_obj.submit_to_employee()
                    attendace_obj.write({'state': 'submitted'})
                
    '''@api.multi
    def action_validate_attendance_sheet(self):
        attendace_pool = self.env['daily.attendance']
        if self._context.has_key('active_ids'):
            for attendance_id in self._context.get('active_ids'):
                if attendance_id not in [56393,17,54767,54781,54764,55504,89266,98041,55384,56426,54897,55375,55675,55230,55343,55002,136281,]:
                    attendace_obj = attendace_pool.browse(attendance_id)
                    if attendace_obj.state == 'submitted':
                        #attendace_obj.attendance_validate()
                        attendace_obj.write({'state': 'validate'})
                        attendace_obj.class_id.write({'state': 'done'})'''
                
            
    
    # For create a timesheet based on the class duration
    #@api.model
    #@api.multi
    
    def submit_to_employee(self):
        # If timesheet already created then it open a pop-up and you can submit the timesheet but did't create any timesheet for twice
        new_user_id = self.teacher_id.user_id and self.teacher_id.user_id.id
        tz = self.env.user.partner_id.tz and pytz.timezone(self.env.user.partner_id.tz)  or pytz.utc
        start_time = pytz.utc.localize(datetime.strptime(self.class_id.start_time, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        end_time = pytz.utc.localize(datetime.strptime(self.class_id.end_time, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        
        if self.student_ids:
            if self.total_presence == 0 and self.total_absent == 0:
                self.write({'state': 'draft'})
            else:
                if self.total_student == self.total_absent:
                    self.write({'state': 'cancelled'})
                else:
                    if self.total_presence == 0 and self.total_absent > 0:
                        self.write({'state': 'cancelled'})
                    else:
                        if new_user_id:
                            self.env.cr.execute('''
                                SELECT id
                                FROM hr_timesheet_sheet_sheet
                                WHERE (date_from <= %s and %s <= date_to)
                                AND user_id=%s''',(end_time.date(), start_time.date(), new_user_id))
                            timesheet_id = self.env.cr.fetchall()
                            temp = 0
                            if timesheet_id:
                                temp = 1
                                timesheet_obj = self.env['hr_timesheet_sheet.sheet'].sudo().browse(int(timesheet_id[0][0]))
                                timesheet_line_id = self.env['account.analytic.line'].sudo().search([('sheet_id','=',timesheet_id[0][0])])
                                if timesheet_obj:
                                    unit_amount = 0.0
                                    for linked_attendance in timesheet_obj.attendance_ids:
                                        att_start_time = pytz.utc.localize(datetime.strptime(linked_attendance.class_id.start_time, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
                                        att_end_time = pytz.utc.localize(datetime.strptime(linked_attendance.class_id.end_time, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
                                        if (start_time >= att_start_time and end_time <= att_end_time):
                                            unit_amount = 0.0
                                            break;
                                        else:
                                            if (start_time >= att_start_time and start_time < att_end_time) or (end_time > att_start_time and end_time <= att_end_time):
                                                unit_amount = 0.0
                                                break;
                                            else:
                                                unit_amount = (((end_time - start_time).seconds) / 3600)
                                    if unit_amount > 0:
                                        timesheet_obj.sudo().write({'attendance_ids' : [( 4, self.id)]})
                                    else:
                                        timesheet_obj.sudo().write({'skip_attendance_ids' : [( 4, self.id)]})
                                    if timesheet_line_id:
                                        timesheet_line_id.sheet_id.sudo().action_timesheet_draft()
                                        old_unit_amount = timesheet_line_id.unit_amount
                                        timesheet_line_id.sudo().write({'unit_amount': (unit_amount + old_unit_amount)})
                                    timesheet_obj.sudo().action_timesheet_confirm()
                            if temp == 1:
                                ir_model_obj = self.env['ir.model.data']
                                view = ir_model_obj.get_object_reference('teacher_timesheet', 'view_submit_attendance')
                                view_id = view and view[1] or False
                                res = {
                                    'name': _('Submit Attendance Sheet'),
                                    'type': 'ir.actions.act_window',
                                    'view_type': 'form',
                                    'view_mode': 'form',
                                    'view_id': view_id,
                                    'res_model': 'submit.attendance.wizard',
                                    'target': 'new',
                                    'context': {}
                                }
                                return res
                        
                        # For create a timesheet[In Waiting For Approval state] for the teache based on the class duration on Submit button
                        unit_amount  = (((end_time - start_time).seconds) / 3600)
                        hr_timesheet_sheet = self.env['hr_timesheet_sheet.sheet']
                        account_analytic_line = self.env['account.analytic.line']
                        timesheet_vals = {
                        	'employee_id': self.teacher_id and self.teacher_id.id or False,
                        	'department_id': self.teacher_id.department_id and self.teacher_id.department_id.id or False,
                        	'attendance_id': self and self.id or False,
                        	'attendance_ids': [( 6, 0, [self.id])],
                        	'date_from': start_time.date(),
                        	'date_to': end_time.date()
                        }
                        hr_timesheet_sheet_id = hr_timesheet_sheet.create(timesheet_vals)
                        account_analytic_line_vals = {
                        	'date': start_time,
                        	'name': self.project_id.name +' - '+ self.class_id.name,
                        	'project_id': self.project_id and self.project_id.id or False,
                        	'class_id': self.class_id and self.class_id.id or False,
                            'school_id': self.school_id and self.school_id.id or False,
                        	'unit_amount': unit_amount,
                        	'sheet_id': hr_timesheet_sheet_id and hr_timesheet_sheet_id.id or False,
                        	'sheet_id_computed': hr_timesheet_sheet_id and hr_timesheet_sheet_id.id or False,
                        	# fixed user_id for timesheet computation on salary slips
                        	'user_id': self.teacher_id and self.teacher_id.user_id and self.teacher_id.user_id.id,
                        }
                        account_analytic_line_id = account_analytic_line.create(account_analytic_line_vals)
                        
                        hr_timesheet_sheet_id.sudo().action_timesheet_confirm()
                        
                        # END For create a timesheet for the teache based on the class duration
                        
                        self.write({'state': 'submitted'})
        else:
            self.write({'state': 'draft'})
        return True
    
    @api.multi
    def attendance_validate(self):
        '''Method to validate attendance'''
        sheet_line_obj = self.env['attendance.sheet.line']
        acadmic_year_obj = self.env['academic.year']
        acadmic_month_obj = self.env['academic.month']
        attendance_sheet_obj = self.env['attendance.sheet']
        
        # Timesheet will be automatic approved on Validate button that i created on submit button
        hr_timesheet_sheet = self.env['hr_timesheet_sheet.sheet']
        hr_timesheet_sheet_id = hr_timesheet_sheet.search([('attendance_id','=',self.id)], limit=1)
        if hr_timesheet_sheet_id:
            #if hr_timesheet_sheet_id.state in ['draft','new']:
            hr_timesheet_sheet_id.action_timesheet_done()
        else:
            new_user_id = self.teacher_id.user_id and self.teacher_id.user_id.id
            tz = self.env.user.partner_id.tz and pytz.timezone(self.env.user.partner_id.tz)  or pytz.utc
            date_from = pytz.utc.localize(datetime.strptime(self.class_id.start_time, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
            date_to = pytz.utc.localize(datetime.strptime(self.class_id.end_time, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
            if new_user_id:
                self.env.cr.execute('''
                    SELECT id
                    FROM hr_timesheet_sheet_sheet
                    WHERE (date_from <= %s and %s <= date_to)
                    AND user_id=%s''',(date_to.date(), date_from.date(), new_user_id))
                updated_timesheet_id = self.env.cr.fetchall()
                if updated_timesheet_id:
                    timesheet_obj = self.env['hr_timesheet_sheet.sheet'].browse(updated_timesheet_id[0][0])
                    timesheet_obj.action_timesheet_done()
        # END Timesheet will be automatic approved on Validate button that i created on submit button

        for line in self:
            date = datetime.strptime(line.date, "%Y-%m-%d %H:%M:%S")
            year = date.year
            year_ids = line.academic_year_id
            month_ids = acadmic_month_obj.search([('date_start', '<=', date),
                                                  ('date_stop', '>=', date),
                                                  ('year_id', 'in',
                                                   year_ids.ids)])
            if month_ids:
                for month_id in month_ids:
                    month_data = month_id
                    domain = [('month_id', 'in', month_id.ids),
                              ('year_id', 'in', year_ids.ids)]
                    att_sheet_ids = attendance_sheet_obj.search(domain)
                    attendance_sheet_id = (att_sheet_ids and att_sheet_ids[0] or
                                           False)
                    if not attendance_sheet_id:
                        sheet = {'name':  month_data.name + '-' + str(year),
                                 'standard_id': line.std_id.id,
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
        self.class_id.state = 'done'
        return True
    
