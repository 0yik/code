{
    'name': 'Multi Company Epense Fix',
    'description': 'This module will Modify some rule and add access rights for employee in expense',
    'category': 'Expense',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs',
    'website': 'www.hashmicro.com',
    'depends': ['hr_expense'],
    'data': [
        'security/ir_rule.xml',
    ],
    'application': True,
    'installable': True,
}