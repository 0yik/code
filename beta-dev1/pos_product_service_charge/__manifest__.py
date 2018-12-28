# -*- coding: utf-8 -*-
{
    'name' : 'POS Product Service Charge',
    'version' : '1.0',
    'category': 'Point Of Sale',
    'author': 'HashMicro / MP technolabs / Mital - Bipin Prajapati - Purvi Pandya',
    'description': """POS Sarang oci Buttons.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'acc_sarang_oci_service_charge', 'point_of_sale'],
    'data': [
        'view/service_charge_view.xml',
        'view/template.xml',
    ],
    'demo': [
        
    ],
    'qweb': [
        'static/src/xml/pos_service.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
