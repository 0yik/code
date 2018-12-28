# -*- coding: utf-8 -*-
{
    'name': 'Central Kitchen PO',
    'version': '1.0',
    'category': 'purchase',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'description': """
      Whenever user creates a PO to partner “Central Kitchen” create Sales Order in centralkitchen.equiperp.com  
    """,
    'summary': 'Whenever user creates a PO to partner “Central Kitchen” create Sales Order in centralkitchen.equiperp.com',
    'depends': [
        'purchase',
    ],
    'data': [
        'data/partner_data.xml',
        'views/purchase_order.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
