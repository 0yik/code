import ftplib
import os
import io
from odoo import models, fields, api, _

class Reader:
    def __init__(self):
        self.data = ""
    def __call__(self, s):
        self.data += s

class Emp_attendance_report(models.Model):
    _inherit="hr.attendance"

    @api.multi
    def _cron_import_attendance_automatically(self):
        try:
            attendance_server_host = self.env['ir.values'].get_default('base.config.settings', 'attendance_server_host')
            attendance_port = self.env['ir.values'].get_default('base.config.settings', 'attendance_port')
            attendance_username = self.env['ir.values'].get_default('base.config.settings', 'attendance_username')
            attendance_password = self.env['ir.values'].get_default('base.config.settings', 'attendance_password')
            attendance_file_location = self.env['ir.values'].get_default('base.config.settings', 'attendance_file_location')
            attendance_file_name = self.env['ir.values'].get_default('base.config.settings', 'attendance_file_name')

            ftp = ftplib.FTP()
            ftp.connect(attendance_server_host, attendance_port)
            ftp.login(attendance_username, attendance_password)
            # print ftp.pwd()
            # ftp.cwd(attendance_file_location)
            file_name = attendance_file_name

            file = Reader()
            ftp.retrbinary('RETR ' + file_name, file)
            file_lines = [line for line in file.data.split("\n") if line != ""]
            count_file_lines = len(file_lines)
            hr_employee_obj = self.env['hr.employee']
            for line in file_lines:
                file_emp_id = line[24:28] # employee id
                emp = hr_employee_obj.search([('emp_id', '=', file_emp_id)], limit=1)
                if emp:
                    emp_atten_list = sorted([emp_atten for emp_atten in file_lines if str(emp.emp_id) in emp_atten], key=int)
                    emp_start_date = emp_atten_list[0]
                    emp_end_date = emp_atten_list[-1]

                    date_line = '-'.join([emp_start_date[2:6],emp_start_date[6:8],emp_start_date[8:10]])
                    time_line = ':'.join([emp_start_date[10:12],emp_start_date[12:14],'00'])
                    time_line1 = '.'.join([emp_start_date[10:12],emp_start_date[12:14]])
                    start_date_time = date_line + " " + time_line

                    date_line_end = '-'.join([emp_end_date[2:6],emp_end_date[6:8],emp_end_date[8:10]])
                    time_line_end = ':'.join([emp_end_date[10:12],emp_end_date[12:14],'00'])
                    time_line_end1 = '.'.join([emp_end_date[10:12],emp_end_date[12:14]])
                    end_date_time = date_line_end + " " + time_line_end

                    values = {
                        'employee_id' : emp.id,
                        'check_in' : start_date_time,
                        'check_out' : end_date_time,
                        'date_dt':date_line,
                        'o_timein':time_line1,
                        'o_timeout':time_line_end1,
                        'adj_timein':time_line1,
                        'adj_timeout':time_line_end1,
                    }
                    new_id = self.env['hr.attendance'].sudo().create(values)

                    for emp in emp_atten_list:
                        file_lines.remove(emp)

            file = Reader()
            ftp.retrbinary('RETR ' + file_name, file)
            count_new_file_lines = len([line for line in file.data.split("\n") if line != ""])
            if count_new_file_lines == count_file_lines:
                bio = io.BytesIO('\n'.join(file_lines))
                ftp.storbinary('STOR ' + file_name, bio)
            file = Reader()
            ftp.retrbinary('RETR ' + file_name, file)
            ftp.close()
        except ValueError:
            pass
        return True
