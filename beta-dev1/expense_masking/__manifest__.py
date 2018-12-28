# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Expense Masking',
    'version': '1.0',
    'category': 'Web',
    'summary': 'Changing of workflow for Odoo 10 Expense Claims module. Users to create Expense Claims using Expense Report by entering the lines. Each of the lines will then create a Expense to Submit record.',
    'description': """
    
    """,
    'author':'Hashmicro / Quy',
    'depends': ['base','hr_expense'],
    'data': [
        'views/hr_expense_sheet_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
