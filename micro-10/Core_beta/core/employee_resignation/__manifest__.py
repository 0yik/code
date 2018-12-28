# -*- coding: utf-8 -*-
{
    'name': "Resignation Management",

    'summary': """
        Resignation management.
    """,

    'description': """
        Resignation management.\n
        1. Employee can submit resignation request.\n
        2. Manager can approve or reject the resignation request.
    """,

    'author': "HashMicro/ Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'employee_notice_period', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/email_template.xml',
        'data/ir_sequence_data.xml',
        'wizard/change_notice_period_view.xml',
        'views/resignation_request_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
