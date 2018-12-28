{
    'name': 'Propel Modifier Hierarchy',
    'description': 'This module will add Propel Modifier Hierarchy.',
    'category': 'Leave Management',
    'version': '1.0',
    'author': 'HashMicro / Janbaz Aga',
    'website': 'www.hashmicro.com',
    'depends': ['hr_holidays'],
    'data': [
        'security/hr_holidays_security.xml',
        'security/ir.model.access.csv',
        'views/hr_holidays.xml',
        'data/hr_data.xml',
    ],
    'application': True,
    'installable': True,
}