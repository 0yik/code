# -*- coding: utf-8 -*-
{
    'name': 'Request Price To Engineer',
    'version': '1.1',
    'category': 'Request Price',
    'summary': 'Request Price To Engineer',
    
    'depends': [
        'job_cost_estimate_customer','crm'
    ],
    
    'data': [
        'views/request_price_view.xml',
        'security/ir.model.access.csv'
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
