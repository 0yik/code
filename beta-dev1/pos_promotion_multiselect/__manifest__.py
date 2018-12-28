# -*- coding: utf-8 -*-
{
    'name' : 'POS Promotion Multiselection',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro / MP technolabs - Komal Kaila',
    'description': """POS Promotion Multiselection.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_promotion'],
    'data': [
        'security/ir.model.access.csv',
        'data/promotion_days_data.xml',
        'views/promotion.xml',
       'views/pos_promotion_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
	   # 'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
