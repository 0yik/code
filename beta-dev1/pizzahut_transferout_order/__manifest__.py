# -*- coding: utf-8 -*-
{
    'name' : 'Pizzahut Transferout Order',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila',
    'description': """Create Transfer Out order flow.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_bus','pizzahut_modifier_startscreen', 'branch_sales_report'],
    'data': [ 
        'views/pos_all_free_template.xml',
        'views/pos_order_view.xml',
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
