# -*- coding: utf-8 -*-
{
    'name' : 'auto_invoice_basedon_tax',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / Duy',
    'description': """auto_invoice_basedon_tax.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','sale','account'],
    'data': [
        # 'view/sale_view.xml'
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
