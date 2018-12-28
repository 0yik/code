# -*- coding: utf-8 -*-
{
    'name': "Employee Breaktime",
    'description': """ Manage employee breaktime """,
    'author': "HashMicro / Mp Technolabs / Vatsal",
    'website': "http://www.hashmicro.com",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': ['web','hr_attendance','hr','sg_hr_employee','report', 'barcodes'],
    'data': [
        'views/web_asset_backend_template.xml',
        'views/emp_breaktime_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'qweb': [
        "static/src/xml/breaktime.xml",
    ],
}