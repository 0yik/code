{
    'name': 'Multi Company Epense Fix',
    'description': 'This module will Modify some rule and add access rights for employee in expense',
    'category': 'Expense',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs',
    'website': 'www.hashmicro.com',
    'depends': ['hr_expense','hr_leave_balance'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
    'installable': True,
}