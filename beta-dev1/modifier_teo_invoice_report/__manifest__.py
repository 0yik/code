# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Credit/Debit Note Report",

    'summary': """
        Credit/Debit Note Report for TEO Garment
    """,
    'description': """
    """,

    'author': "HashMicro / Bhavin",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant','modifier_teo_sale_order','modifier_teo_accounting'],

    # always loaded
    'data': [
        'report_menu.xml',
        'report/layouts.xml',
        'report/invoice_report.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}