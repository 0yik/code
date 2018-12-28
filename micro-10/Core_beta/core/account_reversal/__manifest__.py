# -*- coding: utf-8 -*-
{
    "name": "Account Reversal (V10C)",
    "summary": "Wizard for creating a reversal account move",
    "category": "Accounting & Finance",
    "website": "https://odoo-community.org/",
    "author": "Akretion,"
              "Camptocamp,"
              "ACSONE SA/NV,"
              "Tecnativa,"
              "Khaled Hamed,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'version': '10.0.1.0',
    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'wizard/account_move_reverse_view.xml',
        'views/account_move_view.xml',

    ],
}
