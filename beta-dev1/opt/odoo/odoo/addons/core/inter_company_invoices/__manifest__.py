# -*- coding: utf-8 -*-
# © 2013-Today Odoo SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Inter Company Module for Invoices',
    'description':"""
    Allow intercompany transaction between companies in the system, 
    allowing 2 companies in the same system to be able to create invoices for each other
    """,
    'category': 'Accounting & Finance',
    'website': 'www.hashmicro.com',
    'author': 'HashMicro / Abishek',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account_accountant',
        'account'
    ],
}
