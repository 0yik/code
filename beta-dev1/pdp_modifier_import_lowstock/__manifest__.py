# -*- coding: utf-8 -*-
{
    'name' : 'PDP Modifier Import Lowstock',
    'version' : '1.0',
    'category': 'sale',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Trivedi',
    'description': """ Import Product with Qty
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'stock', 'low_stock_notification', 'product', 'purchase',
    ],
    'data': [
    'wizard/import_product.xml',
    'views/low_stock_notification_view.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
