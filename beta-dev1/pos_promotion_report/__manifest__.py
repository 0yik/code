# -*- coding: utf-8 -*-
{
    'name': "pos_promotion_report",

    'summary': """
        POS Promotion Report""",

    'description': """
        Module for POS Promotion Report
    """,

    'author': "HashMicro / Hoang",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'point_of_sale',
        'stock',
        'pos_promotion',
        'pos_order_branch',
        'brand_sales_report'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_promotion_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}