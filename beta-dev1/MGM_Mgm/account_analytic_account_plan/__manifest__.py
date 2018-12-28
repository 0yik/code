# -*- coding: utf-8 -*-
{
    'name': "account_analytic_account_plan",

    'description': """
        Long description of module's purpose
    """,

    'author': "HashMicro/Duy",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'analytic', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/analytic_category_views.xml',
        'views/account_analytic_view.xml',
        'views/analytic_distribution_view.xml',
        'views/sale_order_line_view.xml',
        'views/account_invoice_line_view.xml',
        'views/purchase_order_line.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}