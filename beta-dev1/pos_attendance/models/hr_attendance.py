from odoo import api, models, fields, exceptions, _
from datetime import datetime

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    flag = fields.Boolean('Flag', default=False)
    
    @api.multi
    def check_user_access(self, password, login):
        user = self.env['res.users'].search([('login','=',login),('temp_password','=',password)])
        print "========datetime.now().strftime('%H:%M:%S')===========",datetime.now().strftime('%H:%M:%S')
        result = {'user' : user.name, 'check_time' : str(datetime.now().strftime('%H:%M:%S'))}
        if not user:
            result['title'] = 'Invalid Username or Password'
            result['warning'] = 'Invalid Username or Password'
            return result
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
        if not employee:
            result['title'] = 'Employee does exist with this user'
            result['warning'] = 'Employee does exist with this user'
            return result
        if len(employee.ids) > 1:
            result['title'] = 'Warning'
            result['warning'] = 'This user is associated with more then 1 employee! Please contact your administrator'
            return result
        result['employee'] = employee.id
        return result

    @api.multi
    def create_attendance(self, password, login):
        result = self.check_user_access(password,login)
        if result.get('warning',False):
            return result
        last_action = self.env['hr.attendance'].search([('employee_id','=',result.get('employee',False))])
        if last_action:
            max_att_id = max(last_action.ids)
            last_attendance = self.env['hr.attendance'].browse(max_att_id)
            if last_attendance.check_in and  not last_attendance.check_out:
                last_attendance.check_out = fields.Datetime.now()
                result['action'] = 'Checked out at '
                result['msg'] = 'Goodbye '
            else:
                self.create({'employee_id':result.get('employee',False),
                             'check_in' : fields.Datetime.now(),
                             })
                result['action'] = 'Checked in at '
                result['msg'] = 'Welcome '
        else:
            self.create({'employee_id':result.get('employee',False),
                         'check_in' : fields.Datetime.now(),
                         })
            result['action'] = 'Checked in at '
            result['msg'] = 'Welcome '
        return result
