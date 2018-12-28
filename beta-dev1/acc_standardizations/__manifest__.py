# -*- coding: utf-8 -*-
{
    'name': "Account Standarised",

    'summary': """
        Added new field for payment reference in account payment form.""",

    'description': """
        Added new field for payment refrence in paymet popup.
        Added new report in payment.
    """,

    'author': "HashMicro / Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/account_payment_view.xml',
        'views/report.xml',
        'views/report_payment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
}
