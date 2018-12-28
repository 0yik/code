# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ReportEmpAttendance(models.AbstractModel):
    _name = 'report.hr_attendance_overtime.report_epmloyee_attendance'

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
                        'emp_number': one_employee.identification_id or '',
                        'emp_name': one_employee.name or '',
                        'emp_department': one_employee.department_id and one_employee.department_id.name or '',
                    }
                    employees_data.append(one_employee_dict)

                    hr_timesheet_sheet_obj = self.env['hr_timesheet_sheet.sheet'].sudo()
                    timesheet_recs = False
                    if docs.from_date and docs.to_date:
                        timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id),
                            ('date_from', '<=', docs.from_date), ('date_to', '>=', docs.to_date)])
                    elif docs.from_date:
                        timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id),
                            ('date_from', '<=', docs.from_date)])
                    elif docs.to_date:
                        timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id),
                            ('date_to', '>=', docs.to_date)])
                    else:
                        timesheet_recs = hr_timesheet_sheet_obj.search([('employee_id', '=', one_employee.id)])

                    hr_timesheet_sheet_day_obj = self.env['hr_timesheet_sheet.sheet.day'].sudo()
                    attendance_recs = False
                    if timesheet_recs:
                        if docs.from_date and docs.to_date:
                            attendance_recs = hr_timesheet_sheet_day_obj.search([('employee_id', '=', one_employee.id),
                                 ('sheet_id', 'in', timesheet_recs.ids), ('name', '<=', docs.from_date), ('name', '>=', docs.to_date)], order='name')
                        elif docs.from_date:
                            attendance_recs = hr_timesheet_sheet_day_obj.search([('employee_id', '=', one_employee.id),
                            ('sheet_id', 'in', timesheet_recs.ids), ('name', '<=', docs.from_date)], order='name')
                        elif docs.to_date:
                            attendance_recs = hr_timesheet_sheet_day_obj.search([('employee_id', '=', one_employee.id),
                            ('sheet_id', 'in', timesheet_recs.ids),('name', '>=', docs.to_date)], order='name')
                        else:
                            attendance_recs = hr_timesheet_sheet_day_obj.search([('employee_id', '=', one_employee.id), ('sheet_id', 'in', timesheet_recs.ids)], order='name')

                    attendances = []
                    total_attendance = 0.00
                    # for one_timesheet in timesheet_recs:
                        # for one_attendance in one_timesheet.period_ids:
                    for one_attendance in attendance_recs:
                        total_attendance += one_attendance.total_attendance
                        attendances.append({
                            'att_obj': one_attendance,
                            'date': one_attendance.name or '',
                            'total_attendance':"%.2f" % one_attendance.total_attendance or 0.00,
                            'early': "%.2f" % one_attendance.early or 0.00,
                            'late': "%.2f" % one_attendance.late or 0.00,
                            'undertime': "%.2f" % one_attendance.undertime or 0.00,
                            'ot1_hours': "%.2f" % one_attendance.ot1_hours or 0.00,
                            'ot1_5_hours': "%.2f" % one_attendance.ot1_5_hours or 0.00,
                            'ot2_hours': "%.2f" % one_attendance.ot2_hours or 0.00,
                        })
                    one_employee_dict.update({
                        # 'attendances': sorted(attendances, key=lambda item: item['date']),
                        'attendances': attendance_recs,
                        'total_attendance': "%.2f" % total_attendance,
                    })
                print "------employees_data----",employees_data

                period = None
                if docs.from_date and docs.to_date:
                    period = "From " + str(docs.from_date) + " To " + str(docs.to_date)
                elif docs.from_date:
                    period = "From " + str(docs.from_date)
                elif docs.from_date:
                    period = " To " + str(docs.to_date)
                docargs = {
                   'doc_ids': self.ids,
                   'doc_model': self.model,
                   'docs': docs,
                   'employees_data': employees_data,
                   'period': period,
                }
                return self.env['report'].render('hr_attendance_overtime.report_epmloyee_attendance', docargs)
