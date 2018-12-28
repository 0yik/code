# -*- coding: utf-8 -*-
{
    'name' : 'Multi uom auto pricing',
    'version' : '1.0',
    'category': 'Point of sale',
    'author': 'HashMicro / MP technolabs / Parikshit Vaghasiya',
    'description': """Modify the auto price in product form.
    """,
    'website': 'www.hashmicro.com',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_multi_auto_pricing_view.xml',
    ],
    'demo': [
    ],
    # 'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
