# -*- coding: utf-8 -*-
{
    'name': "delivery_charges",

    'summary': """
        Add some charge to sale order""",

    'description': """
        Add some charge to sale order
    """,

    'author': "HashMicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/pos_templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}