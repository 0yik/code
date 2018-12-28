# -*- coding: utf-8 -*-

{
    'name': "Employee Contract Hours and Overtime in Timesheet",
    'version': '10.0.1.0.0',
    'author': 'Hashmicro/Abulkasim Kazi',
    'website': "http://www.hashmicro.com",
    'company': 'Hashmicro',
    'summary': 'Enhance the module to pull “Contract Hours” from Payroll >> Contract and calculate “Overtime”.',
    'description': """Enhance the module to pull “Contract Hours” from Payroll >> Contract and calculate “Overtime”.
                   Enhance the module to calculate Overtime by OT1.0, OT 1.5 and OT 2.0.""",
    'category': 'Human Resources',
    'depends': [
        'hr_timesheet_sheet',
        'hr_attendance',
        'hr_timesheet_attendance',
        'hr_contract',
        'hr_holidays',
        'sg_hr_config',
        'payslip_ytd',
    ],
    'data': [
        'report/report_epmloyee_attendance.xml',
        'wizard/attendance_report.xml',
        'views/res_company.xml',
        'views/hr_timesheet_sheet_day.xml',
        'views/hr_config_setting_view.xml',
        'views/hr_payslip.xml',
    ],
    'installable': True,
    'application': True,

}
