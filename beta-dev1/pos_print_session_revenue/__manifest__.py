# -*- coding: utf-8 -*-
{
    'name': "pos_print_session_revenue",

    'summary': """
        print all revenue from point of sales in one POS session""",

    'description': """
        print all revenue from point of sales in one POS session
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/print_session.xml',
    ],
}