# -*- coding: utf-8 -*-
{
    'name': "aikchin_modifier_last_sold_price",

    'summary': """
        Modify the fields""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Hashmicro/ Sang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account','point_of_sale', 'sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_modifier_views.xml',
        'views/account_invoice_modifier_views.xml',
        'views/pos_order_line_modifier_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}