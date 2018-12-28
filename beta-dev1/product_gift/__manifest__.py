# -*- coding: utf-8 -*-
{
    'name': "product_gift",

    'summary': """
        create start/special remarks in quotation.""",

    'description': """
        Last Updated 23 Nov 2017
        create start/special remarks in quotation.
    """,

    'author': "hashmicro/ Luc / Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale', 'aikchin_modifier_last_sold_price'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/product_template_view.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}