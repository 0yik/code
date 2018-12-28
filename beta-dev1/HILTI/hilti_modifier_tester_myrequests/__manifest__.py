# -*- coding: utf-8 -*-
{
    'name': "hilti_modifier_tester_myrequests",

    'summary': """ """,

    'description': """
        Leave and Overtime request.
    """,

    'author': "HILTI/Nitin",
    'website': "http://www.hilti.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Leave and overtime request',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/request_group.xml',
        'data/ir_sequence_data.xml',
        'views/my_request_views.xml',
    ],
    # only loaded in demonstration mode
}