# -*- coding: utf-8 -*-
{
    'name': "payment_tab_invoices",



    'description': """
         Add payment tab in Odoo 10 for cust & supplier invoice
    """,

    'author': "HashMicro/Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
    ],

    # always loaded
    'data': [
        'views/account_invoice_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}