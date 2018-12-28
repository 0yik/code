# -*- coding: utf-8 -*-
{
    'name' : 'Purchase Menu Items',
    'version' : '1.0',
    'category': 'HR',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Purchase Menu Items.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'purchase', 'purchase_request', 'purchase_requisition', 'purchase_tender_comparison', 'bi_generic_import'],
    'data': [
		'view/purchase_view.xml', 
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
