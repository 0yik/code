# -*- coding: utf-8 -*-
{
    'name': "transfer_out_POS",

    'summary': """
        Register Payment from POS Screen""",

    'description': """
        Register Payment from POS Screen
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'pos_restaurant', 'pizzahut_modifier_startscreen'],

    # always loaded
    'data': [
        'views/pos_delivery_templates.xml',
    ],
    # only loaded in demonstration mode
    'qweb': ['static/src/xml/transfer_out.xml'],
}