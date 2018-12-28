# -*- coding: utf-8 -*-
{
    'name': 'Reorder Sales',
    'version': '1.0',
    'category': 'sales',
    'author': 'HashMicro/ MPTechnolabs - Komal Kaila',
    'website': "http://www.hashmicro.com",
    'summary': 'Reorder Sales',
    'depends': [
        'purchase','point_of_sale', 'centralkitchen_po',
    ],
    'data': [
        'data/res_partner_data.xml',
        'views/purchase_config_view.xml',
        'wizard/reorder_po_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
