# -*- coding: utf-8 -*-
{
    'name' : 'Bank Details Improting',
    'version' : '1.0',
    'category': 'sale',
    'author': 'HashMicro',
    'description': """Enables the bank branches master and enable the option to import bank details and bank branches details.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['sale_commission_target_gt', 'hm_sales_standardization', 'hr_payroll'],
    'data': [
        'view/hr_employee.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
