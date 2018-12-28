{
    'name': 'Province Wage Range',
    'description': 'This module is to set min and max wage for state/province.',
    'category': 'HR',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs (Chankya)',
    'website': 'www.hashmicro.com',
    'depends': ['hr_payroll', 'sales_team'],
    'data': [
        'views/province_wage_range_view.xml',
    ],
    'application': True,
    'installable': True,
}