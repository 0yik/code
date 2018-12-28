# -*- coding: utf-8 -*-
{
    'name': 'POS Rental',
    'version': '2.1',
    'summary': 'Sell Product as Rent',
    'description': """
POS Rental
================================
    """,
    'author': 'HashMicro/Kunal/Dhaval',
    'category': 'Point of Sale',
    'depends': ['point_of_sale','stock','product_booking_ccm','reusable_invoice_digitalsignature', 'reusable_pos_deleteorderline'],
    'data': [
        'views/templates.xml',
        'views/models_view.xml',
        'views/pos_session_view.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/list_field_image.xml',
        'static/src/xml/pos.xml',
    ],
    'installable': True,
}
