# -*- coding: utf-8 -*-
{
    'name' : 'Multiple Customer Delivery Address',
    'version' : '1.0',
    'category': 'HR',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Multiple Customer Delivery Address
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'sale','purchase_request'],
    'data': [
		'view/sale_view.xml',
		'view/res_partner_view.xml',
        'view/customer_invoice_view.xml',
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
