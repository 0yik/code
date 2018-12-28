# -*- coding: utf-8 -*-
{
    'name': "mitsuyoshi_modifier_sales_menu",

    'summary': """
        Modifier Field""",

    'description': """
        This module modifies menu item Blanket Order => Sales Forecast, Quotation => Draft PO Customer,Sales Order => PO Customer 
    """,

    'author': "Rajnish",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','so_blanket_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}