from odoo import models, fields,api
import datetime,pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta,time

class salary_rule(models.Model):
    _inherit ='hr.salary.rule'

    # amount  = fields.Float('Amount')
    late    = fields.Integer('Late (in minutes)')

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_sheet(self):
        res = super(hr_payslip, self).compute_sheet()
        if self.date_from and self.date_to and self.employee_id:
            days = datetime.datetime.strptime(self.date_to,DEFAULT_SERVER_DATE_FORMAT) - datetime.datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT)
            late_deduct = 0
            count = 0
            late_rule = self.env['hr.salary.rule'].search([('name', '=', 'Late'), ('code', '=', 'LATE')])
            for i in range(0,days.days +1):
                day = datetime.datetime.strptime(self.date_from,DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=i)
                branch_timesheet    = self.env['branch.timesheet'].search([('state','=','done')])
                time_line           = self.env['branch.timesheet.line'].search([('branch_sheet_id','in',branch_timesheet.ids),('date','=',day.strftime(DEFAULT_SERVER_DATE_FORMAT)),('employee_id','=',self.employee_id.id)])
                attendance_ids       = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id)])
                if time_line and attendance_ids:
                    attendance_id = attendance_ids.filtered(lambda record: datetime.datetime.strptime(record.check_in,DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT) == day.strftime(DEFAULT_SERVER_DATE_FORMAT))
                    if attendance_id:
                        time_start = '{0:02.0f}:{1:02.0f}:00'.format(*divmod(time_line[-1].from_hours * 60, 60))
                        timezone_tz = 'Singapore'
                        if self._context.get('tz', 'False'):
                            timezone_tz = self._context.get('tz', 'utc')
                        local = pytz.timezone(timezone_tz)
                        check_in = pytz.utc.localize(datetime.datetime.strptime(str(attendance_id[0].check_in), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).strftime('%H:%M:%S')
                        time_late = datetime.datetime.strptime(check_in,'%H:%M:%S') - datetime.datetime.strptime(time_start,'%H:%M:%S')
                        if late_rule and (time_late.seconds >= (late_rule.late * 60)):
                            # late_deduct += late_rule.amount
                            late_deduct += late_rule.amount_fix
                            count +=1
            if late_rule.id in self.struct_id.rule_ids.ids:
                self.env['hr.payslip.line'].search([('slip_id','=',self.id),('name','=','Late'),('code','=','LATE')]).write({
                    # 'name'      : 'Late',
                    # 'code'      : 'LATE',
                    # 'salary_rule_id'  : late_rule.id,
                    # 'category_id'  : late_rule.category_id.id,
                    'quantity'  : count,
                    'total'     : late_deduct,
                    'amount'    : late_rule.amount_fix
                })

        return res