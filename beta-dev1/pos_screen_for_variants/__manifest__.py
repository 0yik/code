# -*- coding: utf-8 -*-
{
    'name': "pos_screen_for_variants",

    'summary': """
        This module intends to have functionality to select variants with showing multiple selection view""",

    'description': """
        This module intends to have functionality to select variants with showing multiple selection view
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'POS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        'views/pos_templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}