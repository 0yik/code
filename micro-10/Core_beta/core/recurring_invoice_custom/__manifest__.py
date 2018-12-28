# -*- coding: utf-8 -*-
{
    'name': "Custom Recurring Invoice",

    'summary': """
        Allow users to setup Recurring Invoice models to auto create invoices""",

    'description': """
    """,

    'author': "Teksys Enterprises",
    'website': "http://www.teksys.in",
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account', 'recurring_invoice'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}