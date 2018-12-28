# -*- coding: utf-8 -*-
{
    'name' : 'pdp_modifier_pricelist',
    'version' : '1.0',
    'category': 'Product',
    'author': 'Hashmicro/Duy',
    'description': 'pdp_modifier_pricelist',
    'website': 'www.hashmicro.com',
    'depends' : ['product', 'sale','pdp_modifier_sales_pricelist','puchase_pricelist'],
    'data': [
        'views/product_pricelist_view.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
