# -*- coding: utf-8 -*-
{
    'name': "Telering Scan Aktivasi imei",

    'summary': """
       Telering Scan Aktivasi imei""",

    'description': """
        This module add the functionality of telering scan aktivasi imei. 
    """,
    'author': 'HashMicro / JustCodify',
    'website': 'www.hashmicro.com',
    'category': 'Inventory',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/scan_aktivasi_imei_view.xml',
        
    ],
}