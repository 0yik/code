# -*- coding: utf-8 -*-
{
    'name' : 'POS Price, Tax and Service Charge Calculation',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila - Purvi Pandya',
    'description': """ """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'acc_sarang_oci_service_charge', 'pos_pin_number', 'pos_supervisor_pin'],
    'data': [ 
        'views/pos_price_charges_registration.xml',
        'views/pos_order_view.xml',
        'views/account_invoice_view.xml',
        'views/product_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
	   'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
