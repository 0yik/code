# -*- coding: utf-8 -*-
{
    'name': "leave_off_in_lieu",

    'summary': """
        User can allocate Off in Lieu and specify the leave will expired after number of days.""",

    'description': """
        User can allocate Off in Lieu and specify the leave will expired after number of days.
    """,

    'author': "Rajnish",
    'website': "http://www.linescripts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sg_allocate_leave','hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}