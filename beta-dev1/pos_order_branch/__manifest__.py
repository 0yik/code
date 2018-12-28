# -*- coding: utf-8 -*-
{
    'name' : 'POS Order and Report with Branch',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs - Bhavin Jethva',
    'description': """ """,
    'website': 'www.hashmicro.com',
    'depends' : ['point_of_sale'],
    'data': [
             'security/ir.model.access.csv',
             'view/pos_order_view.xml',
             'view/service_charge_view.xml',
    ],
    'demo': [
        
    ],
    'qweb':['static/src/xml/pos.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
