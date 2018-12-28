# -*- coding: utf-8 -*-
{
    'name': "Employee Notice Period",

    'summary': """
        Setup and assign notice period for employees.""",

    'description': """
        Setup and assign notice period for employees.
    """,

    'author': "HashMicro/ Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'sg_hr_employee', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'wizard/change_notice_period_view.xml',
        'views/employee_notice_period_view.xml',
        'views/hr_employee_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
