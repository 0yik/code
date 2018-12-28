# -*- coding: utf-8 -*-
{
    'name': 'Expense Approval Matrix',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 17,
    'summary': 'setup for expense approval',
    'description': "This module includes approval for expense based on the given hierarchy.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/ Kannan/ Krupesh',
    'depends': [
        'hr_expense'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/email_template.xml',
        'views/expense_approval_matrix_view.xml',
        'views/hr_expense_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
