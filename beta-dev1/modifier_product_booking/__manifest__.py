# -*- coding: utf-8 -*-
{
    'name': 'Product Bookig Module Modifications',
    'version': '1.0',
    'summary': 'Product booking Changes',
    'description': """
Changed Features
================================
* Change 'Barcode' to 'RFID Code'
* Hide "Delivery Order" button from Booking Order
    """,
    'author': 'HashMicro/Kunal',
    'category': 'Booking',
    'depends': ['product_booking_ccm'],
    'data': [
        'views/models_view.xml',
    ],
    'installable': True,
}
