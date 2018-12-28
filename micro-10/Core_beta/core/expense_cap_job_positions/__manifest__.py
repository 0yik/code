{
    'name': 'Expense Cap Job Positions',
    'version': '1.0',
    'author': 'HashMicro / Mustufa',
    'category': 'Human Resources',
    'sequence': 1,
    'website': 'www.hashmicro.com',
    'depends': [
        'base_setup',
        'resource', 
        'sg_expense_maxcap',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_job.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
