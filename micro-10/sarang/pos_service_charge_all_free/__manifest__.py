# -*- coding: utf-8 -*-
{
    'name' : 'POS Product Service Charge with All Free',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Purvi Pandya',
    'description': """When All Free is On then Service Charge will be disables.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'pos_all_free', 'pos_product_service_charge'],
    'data': [
        'view/template.xml',
    ],
    'demo': [
        
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
