# -*- coding: utf-8 -*-
{
    'name': "Mitsuyoshi Modifier Import Sale",

    'summary': """
    To add Import function to add multiple products in Quotation, Sales Order, Sales Forecast
    """,

    'description': """
        To add Import function to add multiple products in Quotation, Sales Order, Sales Forecast
    """,

    'author': "HashMicro/Quy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','so_blanket_order'

                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/import_sale.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}