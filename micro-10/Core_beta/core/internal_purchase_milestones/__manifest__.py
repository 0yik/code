# -*- coding: utf-8 -*-
{
    'name': 'Internal Purchase Milestones',
    'version': '1.0',
    'summary': 'Purchase milestone processing',
    'description': 'Enhance the purchase module by adding the purchase milestones function',
    'author': 'Hashmicro / Saravanakumar',
    'website': 'http://www.hashmicro.com',
    'category': 'purchase',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/work_order_view.xml',
        'views/purchase_view.xml',
        'views/invoice_view.xml',
        'data/sequence_data.xml',
    ],
    'installable': True,
    'application': True,
}

