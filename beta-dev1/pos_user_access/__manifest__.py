# -*- coding: utf-8 -*-
{
    'name': "pos_user_access",

    'summary': """
        Control the access of user to minus function.""",

    'description': """
        Control the access of user to minus function.
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'pos_user_access_mac5'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_access_views.xml',
        'views/pos_user_access_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}