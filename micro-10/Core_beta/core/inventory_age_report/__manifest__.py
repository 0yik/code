# -*- coding: utf-8 -*-
{
    'name': "Stock Aging Report",

    'summary': """
        Apps will print Stock Aging Report by Compnay, Warehoouse, Location, Product Category and Product.""",

    'description': """
        Apps will print Stock Aging Report by Compnay, Warehoouse, Location, Product Category and Product.
    """,

    'author': "Devintelle Soluation, HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HashMicro',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        'delivery',
        'mrp',
        'account',
        'sale_stock',
        # 'multi_company',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_ageing_view.xml',
        'wizard/inventory_wizard_view.xml',
        'report/report_stockageing.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 29.0,
    'currency': 'EUR',
}