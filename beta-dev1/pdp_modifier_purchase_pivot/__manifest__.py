# -*- coding: utf-8 -*-
{
    'name' : 'pdp Modifier Purchase Pivot',
    'version' : '1.0',
    'category': 'purchase',
    'author': 'Hashmicro/GYB IT SOLUTIONS-Anand',
    'description': """ Add fields in Purchase Order Pivot view 
    """,
    'website': 'http://www.hashmicro.com/',
    'depends' : [
	'sale', 'purchase', 'product','PDP_modifier_Product', 'inventory_on_purchase',
    ],
    'data': [
    'views/purchase.xml',
    'views/pdp_modifier_purchase_pivot.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
