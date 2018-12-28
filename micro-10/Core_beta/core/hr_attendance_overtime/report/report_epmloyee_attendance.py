# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ReportEmpAttendance(models.AbstractModel):
    _name = 'report.hr_attendance_overtime.report_epmloyee_attendance'

    def return_date(self, date):
        return datetime.strftime(datetime.strptime(str(date), '%Y-%m-%d'), '%d/%m/%Y') or ''

    def get_time(self, value):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(value * 60, 60)) or 0.00

    @api.model
    def render_html(self, docids, data=None):
        """we are overwriting this function because we need to show values from other models in the report
        we pass the objects in the docargs dictionary"""

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        if docs and docs.select_emp_dep:
            hr_emp_obj = self.env['hr.employee'].sudo()
            employees_ids = []
            if docs.select_emp_dep == 'department' and docs.department_ids:
                for one_department in docs.department_ids:
                    employees_ids.extend(hr_emp_obj.search([('department_id', '=', one_department.id)]).sudo().ids)

            if docs.select_emp_dep == 'employee' and docs.employees_ids:
                employees_ids = docs.employees_ids.sudo().ids

            list(set(employees_ids))
            if employees_ids:
                employees = hr_emp_obj.search([('id','in', employees_ids)])
                employees_data = []
                for one_employee in employees:
                    one_employee_dict = {
                        'company_name': (one_employee.company_id and one_employee.company_id.name) or self.env.user.company_id.name or '',
                        'emp_number': one_employee.emp_id or '',
                        'emp_name': one_employee.name or '',
                        'emp_department': one_employee.department_id and one_employee.department_id.name or '',
                    }

                    # hr_timesheet_sheet_obj = self.env['hr_timesheet_sheet.sheet'].sudo()
                    # timesheet_recs = False
                    # if docs.from_date and docs.to_date:
                    #     timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id),
                    #         '|', ('date_from', '>=', docs.from_date), ('date_to', '<=', docs.to_date)])
                    # elif docs.from_date:
                    #     timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id),
                    #         '|', ('date_from', '<=', docs.from_date), ('date_to', '>=', docs.from_date)])
                    # elif docs.to_date:
                    #     timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id),
                    #         '|', ('date_from', '<=', docs.to_date), ('date_to', '>=', docs.to_date)])
                    # else:
                    #     timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id)])
                    #
                    # hr_timesheet_sheet_day_obj = self.env['hr_timesheet_sheet.sheet.day'].sudo()
                    # attendance_recs = False
                    # if timesheet_recs:
                    #     if docs.from_date and docs.to_date:
                    #         attendance_recs = hr_timesheet_sheet_day_obj.search([
                    #         ('sheet_id', 'in', timesheet_recs.ids), ('name', '>=', docs.from_date), ('name', '<=', docs.to_date)], order='name')
                    #     elif docs.from_date:
                    #         attendance_recs = hr_timesheet_sheet_day_obj.search([
                    #         ('sheet_id', 'in', timesheet_recs.ids), ('name', '>=', docs.from_date)], order='name')
                    #     elif docs.to_date:
                    #         attendance_recs = hr_timesheet_sheet_day_obj.search([
                    #         ('sheet_id', 'in', timesheet_recs.ids),('name', '<=', docs.to_date)], order='name')
                    #     else:
                    #         attendance_recs = hr_timesheet_sheet_day_obj.search([('sheet_id', 'in', timesheet_recs.ids)], order='name')

                    query = "select id from hr_timesheet_sheet_sheet where employee_id = " + str(one_employee.id)
                    self._cr.execute(query)
                    existing_ids = [x[0] for x in self._cr.fetchall()]

                    total_attendance = total_1_attendance = total_1_5_attendance = total_2_attendance = 0.00
                    attendances = []
                    if existing_ids:
                        date_from = docs.from_date
                        date_to = docs.to_date
                        hr_timesheet_sheet_day_obj = self.env['hr_timesheet_sheet.sheet.day'].sudo()
                        existing_att_ids = []
                        if docs.from_date and docs.to_date:
                            query = "select id from hr_timesheet_sheet_sheet_day " \
                                "where sheet_id in (" + ','.join(map(str, existing_ids)) + ") and " \
                                "name >= '" + date_from +"' and  name <= '" + date_to + "'"
                            self._cr.execute(query)
                            existing_att_ids = [x[0] for x in self._cr.fetchall()]
                        elif docs.from_date:
                            query = "select id from hr_timesheet_sheet_sheet_day " \
                                "where sheet_id in (" + ','.join(map(str, existing_ids)) + ") and " \
                                "name >= '" + date_from + "'"
                            self._cr.execute(query)
                            existing_att_ids = [x[0] for x in self._cr.fetchall()]
                        elif docs.to_date:
                            query = "select id from hr_timesheet_sheet_sheet_day " \
                                "where sheet_id in (" + ','.join(map(str, existing_ids)) + ") and " \
                                "name <= '" + date_to + "'"
                            self._cr.execute(query)
                            existing_att_ids = [x[0] for x in self._cr.fetchall()]
                        else:
                            query = "select id from hr_timesheet_sheet_sheet_day " \
                                "where sheet_id in (" + ','.join(map(str, existing_ids)) + ")"
                            self._cr.execute(query)
                            existing_att_ids = [x[0] for x in self._cr.fetchall()]

                        # if attendance_recs:
                        #     for one_attendance in attendance_recs:
                        if existing_att_ids:
                            for one_attendance in hr_timesheet_sheet_day_obj.search([('id', 'in', existing_att_ids)]):
                                total_attendance += one_attendance.total_attendance
                                total_1_attendance += one_attendance.ot1_hours
                                total_1_5_attendance += one_attendance.ot1_5_hours
                                total_2_attendance += one_attendance.ot2_hours
                                attendances.append({
                                    'att_obj': one_attendance,
                                    'date': self.return_date(one_attendance.name) or '',
                                    'total_attendance': self.get_time(one_attendance.total_attendance),
                                    'early': self.get_time(one_attendance.early),
                                    'late': self.get_time(one_attendance.late),
                                    'undertime': self.get_time(one_attendance.undertime),
                                    'ot1_hours': self.get_time(one_attendance.ot1_hours),
                                    'ot1_5_hours': self.get_time(one_attendance.ot1_5_hours),
                                    'ot2_hours': self.get_time(one_attendance.ot2_hours),
                                })

                    one_employee_dict.update({
                        'attendances': sorted(attendances, key=lambda item: item['date']),
                        'total_attendance': self.get_time(total_attendance),
                        'total_1_attendance': self.get_time(total_1_attendance),
                        'total_1_5_attendance': self.get_time(total_1_5_attendance),
                        'total_2_attendance': self.get_time(total_2_attendance),
                    })
                    if attendances:
                        employees_data.append(one_employee_dict)

                if not employees_data:
                    raise ValidationError(_('There is no Attendance found for selected Employees/Departments.'))

                period = None
                if docs.from_date and docs.to_date:
                    period = "From " + self.return_date(docs.from_date) + " to " + self.return_date(docs.to_date)
                elif docs.from_date:
                    period = "From " + self.return_date(docs.from_date)
                elif docs.to_date:
                    period = " To " + self.return_date(docs.to_date)
                docargs = {
                   'doc_ids': self.ids,
                   'doc_model': self.model,
                   'docs': docs,
                   'employees_data': employees_data,
                   'period': period,
                }
                return self.env['report'].render('hr_attendance_overtime.report_epmloyee_attendance', docargs)
            else:
                raise ValidationError(_('There is no Employees found.'))
