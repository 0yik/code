# -*- coding: utf-8 -*-
{
    'name': "absolutepiano_reusable_poscustomer",

    'description': """
        Modifer POS Customer
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/country_code_views.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/pos_customer.xml',
    'static/src/xml/pos_saleorder_line.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}