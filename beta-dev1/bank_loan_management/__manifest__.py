# -*- coding: utf-8 -*-
{
    'name': 'bank_loan_management',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'HashMicro/ MPTechnolabs - Bharat Chauhan',
    'website': "http://www.hashmicro.com",
    'summary': 'This module intends to have a functionality to manage loan from third party, ex: bank.',
    'depends': [
        'account', 'hr_employee_loan', 'branch', 'task_list_manager', 
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/partner_data.xml',
        'data/product_data.xml',
        'data/bank_loan_data.xml',
        'wizard/update_rate_view.xml',
        'views/bank_loan.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
