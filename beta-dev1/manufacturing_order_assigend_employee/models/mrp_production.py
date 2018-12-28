
from odoo import api, fields, models, _, tools
import datetime
import time
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    
    assinged_employee_ids = fields.One2many('assigned.employee','mrp_id','AssignedEmployee')
    
    
class AssignedEmployee(models.Model):
    _name = 'assigned.employee'
    
    @api.multi
    @api.onchange('employee_id')
    def onchange_employee(self):
        hr_employee_obj = self.employee_id
        self.department_id = hr_employee_obj.department_id.id
        self.job_id = hr_employee_obj.job_id.id
        self.calendar_id = hr_employee_obj.calendar_id.id
        
        hr_attendance = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id)])
        hours = 0
        for rec in hr_attendance:
            server_dt = DEFAULT_SERVER_DATETIME_FORMAT
            if rec.check_in and rec.check_out:
                chkin_dt = datetime.datetime.strptime(rec.check_in, server_dt)
                chkout_dt = datetime.datetime.strptime(rec.check_out, server_dt)
                dur = chkout_dt - chkin_dt
                hr_dur = dur.seconds
                additional_mintus = abs((dur.seconds / 60))
                if additional_mintus:
                    add_hrs = abs((additional_mintus/ 60))
                    if add_hrs:
                        hours += add_hrs
            
        self.total_working_hour = hours

    @api.multi
    @api.onchange('project_id')
    def onchange_project(self):
        hr_timesheet = self.env['hr_timesheet_sheet.sheet'].search([('employee_id','=',self.employee_id.id)])
        hours = 0
        for emp_rec in hr_timesheet:
            project_rec = emp_rec.timesheet_ids
            for rec in project_rec:
                if self.project_id.id == rec.project_id.id:
                    hours += rec.unit_amount
        self.total_working_hour = hours

    mrp_id = fields.Many2one('mrp.production','Mrp' , invisible=True)
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Role')
    project_id = fields.Many2one('project.project', 'Project')
    calendar_id = fields.Many2one('resource.calendar', 'Working Time')
    total_working_hour = fields.Char('Total Working Hour')

