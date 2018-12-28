from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from datetime import datetime,timedelta

class HrTimesheetSheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    @api.multi
    def attandance_auto_timesheet(self):
        today = datetime.today()
        print "=================today=====================",today
        active_timesheet = self.env['hr_timesheet_sheet.sheet'].search([('state','=','draft'),('date_from','<=',today),('user_id','=',self.env.uid)])
        for timesheet in active_timesheet:
            attendance_ids = self.env['hr.attendance'].search([('employee_id', '=', timesheet.employee_id.id), 
                                                               ('check_in', '>=', str((today + timedelta(days=-1)).date())),
                                                               ('check_in', '<=', str((today + timedelta(days=-1)).date()))])
            if attendance_ids:
                time = datetime.strptime(attendance_ids[0].check_out,"%Y-%m-%d %H:%M:%S") - datetime.strptime(attendance_ids[0].check_in,"%Y-%m-%d %H:%M:%S")
                hours = int(time.seconds//3600)
                minutes = int((time.seconds//60)%60)
    #                     seconds = int(time.total_seconds() % 60)
                float_time = ('%s.%s'%(hours,minutes))
                timeshet_journal = self.env.ref('stable_hr_timesheet_invoice.timesheet_journal')
                contract_id = self.env['hr.contract'].search([('employee_id','=',timesheet.employee_id.id),('state','in',['draft','open','pending'])])
                if contract_id:
                    account_analytic_line = self.env['account.analytic.line'].create({
                        'name': '/',
                        'journal_id':timeshet_journal.id,
                        'account_id':contract_id.analytic_account_id.id,
                        'unit_amount':float(float_time),
                        'sheet_id':timesheet.id,
                        'date':(today + timedelta(days=-1)).date(),
                        
                    })
            if timesheet.date_to < str(today):
                timesheet.action_timesheet_confirm()
                emp_config = self.env['hr.employee.config.settings'].search([])
                if emp_config:
                    last_record = self.env['hr.employee.config.settings'].browse(max(emp_config.ids))
                    if last_record.timesheet_duration > 0:
                        vals = {
                                'employee_id':timesheet.employee_id.id
                        }
                        new_timesheet = self.env['hr_timesheet_sheet.sheet'].create({
                            'date_from': today,
                            'date_to': today + timedelta(days=last_record.timesheet_duration),
                            'state': 'new',
                            'user_id': self.env.uid,
                            'employee_id': timesheet.employee_id.id,
                        })
