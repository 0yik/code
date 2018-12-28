# -*- coding: utf-8 -*-
{
    'name' : 'Barcode Kisok',
    'version' : '1.0',
    'category': 'HR',
    'author': 'HashMicro / MP technolabs / Mital',
    'description': """Barcode Kisok.
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base', 'hr', 'barcodes', 'hr_attendance', 'stock'],
    'data': [
		'views/barcode_kiosk_view.xml',	
		'views/template.xml',
		'data/ir_sequence.xml',
    ],
    'demo': [
    ],
    'qweb': [
		'static/src/xml/kiosk_barcode_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
