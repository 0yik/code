# -*- coding: utf-8 -*-
{
    'name': 'Aikchin Modifier Expenses Approval',
    'version': '1.0',
    'category': 'Expense',
    'summary': '',
    'description': "Expenses Claims Approval Process: Employees submit expenses claims To be approved by HR Manager To be approved by Expense Manager",
    'website': 'https://www.hashmicro.com',
    'author': 'HashMicro / MP technolabs / Monali',
    'depends': ['hr_expense','aikchin_modifier_access_right'],
    'data': [
	'views/expense_view.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
