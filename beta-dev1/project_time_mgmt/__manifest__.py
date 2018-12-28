# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Time Management',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Project Time Management',
    'description': """
    """,
    'author': 'HashMicro / GeminateCS',
    'website': 'www.hashmicro.com', 
    'depends': [
        'project',
        'hr_timesheet'
    ],
    'data': [
        'security/daily_work_security.xml',
        'security/ir.model.access.csv',
        'data/daily_work_journal_scheduler.xml',
        'views/project_timesheet_view.xml',
        'views/project_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
