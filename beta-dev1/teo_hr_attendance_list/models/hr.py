# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import calendar, pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class HRAttendanceList(models.Model):
    _name = 'hr.attendance.list'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    attendance_list_line = fields.One2many('attendance.list.line','attendance_list_id', string="Attendance List")
    
class AttendanceListLine(models.Model):
    _name = 'attendance.list.line'
    
    def convert_tz_to_utz(self, date):
        check_in_dt = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        local_tz = pytz.timezone(self.env.user.tz or 'UTC')
        check_in_local = check_in_dt.replace(tzinfo = pytz.utc).astimezone(local_tz)
        check_in = datetime.strftime(check_in_local, DEFAULT_SERVER_DATETIME_FORMAT)
        return check_in
    
    @api.multi
    @api.depends('o_timein','o_timeout')
    def _compute_time(self):
        for rec in self:
            day_list = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            day = day_list.index(rec.day) if rec.day in day_list else False
            rec.total_hours = rec.o_timeout - rec.o_timein
            for work_day in rec.attendance_list_id.employee_id.calendar_id.attendance_ids:
                contract_id = self.env['hr.contract'].search([('employee_id', '=', rec.attendance_list_id.employee_id.id),('state','=','open')], order='date_start desc', limit=1)
                if contract_id and contract_id.rate_per_hour:
                    if day == int(work_day.dayofweek):
                        rec.over_time = rec.o_timeout - work_day.hour_to if (rec.o_timeout - work_day.hour_to) > 0.0 else 0.0
                        rec.ot_1_0 = rec.o_timeout - work_day.hour_to if (rec.o_timeout - work_day.hour_to) > 0.0 else 0.0
                    else:
                        rec.over_time = rec.o_timeout - 17.83 if (rec.o_timeout - 17.83) > 0.0 else 0.0
                        rec.ot_1_0 = rec.o_timeout - 17.83 if (rec.o_timeout - 17.83) > 0.0 else 0.0
                else:
                    if int(work_day.dayofweek) not in [5,6]:
                        if day == int(work_day.dayofweek):
                            rec.over_time = rec.o_timeout - work_day.hour_to if (rec.o_timeout - work_day.hour_to) > 0.0 else 0.0
                            rec.ot_1_5 = rec.o_timeout - work_day.hour_to if (rec.o_timeout - work_day.hour_to) > 0.0 else 0.0
                    else:
                        rec.over_time = rec.o_timeout - 17.83 if (rec.o_timeout - 17.83) > 0.0 else 0.0
                        rec.ot_2_0 = rec.o_timeout - 17.83 if (rec.o_timeout - 17.83) > 0.0 else 0.0

    @api.multi
    def _related_hod(self):
        for rec in self:
            hod_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('job_id.name', '=', 'HOD')])
            if hod_id:
                rec.hod_id = hod_id[0].id
    
    attendance_list_id = fields.Many2one('hr.attendance.list',string='Attendance List')
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    hod_id = fields.Many2one("hr.employee", string="HOD", compute='_related_hod')
    check_in = fields.Datetime('Check In')
    check_out = fields.Datetime('Check Out')
    date_dt = fields.Date("Date")
    o_timein = fields.Float("O Timein")
    o_timeout = fields.Float("O Timeout")
    adj_timein =fields.Float("adj_timein")
    adj_timeout = fields.Float("adj_timeout")
    total_hours = fields.Float('Total Hours', compute='_compute_time', store=True)
    over_time = fields.Float('Over Time', compute='_compute_time', store=True)
    ot_1_0 = fields.Float('OT #1.0', compute='_compute_time', store=True)
    ot_1_5 = fields.Float('OT #1.5', compute='_compute_time', store=True)
    ot_2_0 = fields.Float('OT #2.0', compute='_compute_time', store=True)
    day = fields.Char("Day")
    emp_remark = fields.Char("Emp Remark")
    lev_remark = fields.Char("Lev Remark")
    sup_remark = fields.Char("Sup Remark")
    state = fields.Selection([('draft','Draft'),('approved','Approved')], string="status", default='draft')
    
class HRAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    @api.model
    def create(self, values):
        res = super(HRAttendance, self).create(values)
        attendance_list_ids = self.env['hr.attendance.list'].search([('employee_id','=',res.employee_id.id)])
        if attendance_list_ids:
            attendance_list_id = attendance_list_ids[0]
        else:
            attendance_list_id = self.env['hr.attendance.list'].create({'employee_id': res.employee_id.id})
        list_line_id = self.env['attendance.list.line'].create({'attendance_list_id': attendance_list_id.id,
                                                                'attendance_id': res.id,
                                                                'check_in': res.check_in,
                                                                'check_out': res.check_out,
                                                                'day': res.day,
                                                                'date_dt': res.date_dt,
                                                                'o_timein': res.o_timein,
                                                                'o_timeout': res.o_timeout,
                                                                'adj_timein': res.adj_timein,
                                                                'adj_timeout': res.adj_timeout,
                                                                'state': 'draft',
                                                                })
        return res
    
    @api.multi
    def write(self, values):
        attendance_line_ids = self.env['attendance.list.line'].search([('attendance_id','=',self.id)], limit=1)
        if attendance_line_ids:
            attendance_line_ids.write(values)
        return super(HRAttendance, self).write(values)
