# -*- coding: utf-8 -*-
{
    'name': "Modifier Product Variants",
    'description': """
        This module add own warehouse quantity field in product variant tree view.
    """,
    'author': 'HashMicro / MPTechnolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',
    'category': 'Inventory',
    'version': '1.0',
    'depends': ['stock', 'branch','product'],
    'data': [
        'views/modifier_product_variants.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}