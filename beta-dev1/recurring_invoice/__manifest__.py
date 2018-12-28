# -*- coding: utf-8 -*-
{
    'name': "recurring_invoice",

    'description': """
        Allow users to do recurring invoice without Contract
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_views.xml',
        'data/ir_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}