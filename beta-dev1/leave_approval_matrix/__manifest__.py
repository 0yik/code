# -*- coding: utf-8 -*-
{
    'name': "Leave Approval Matrix",

    'description': """
        Leave Approval Matrix
    """,

    'author': "HashMicro/ Quy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sg_hr_employee'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/leave_approval_matrix_view.xml',
        'views/hr_job_view.xml',
        'views/leave_request_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}