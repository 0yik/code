# -*- coding: utf-8 -*-
{
    'name': "sales_inventory_summary",

    'summary': """
        sales_inventory_summary""",

    'description': """
        Salespeople can view Inventory Summary by individual and consolidated Locations at Quotations and Sales Order.
    """,

    'author': "Hashmicro / Luc",
    'website': "http://www.Hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/inventory_view.xml',
        'views/inventory_summary_view.xml',
        'static/src/xml/inventory_summary.xml',

    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}