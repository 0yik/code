# -*- coding: utf-8 -*-
{
    'name': 'Payment QR Code',
    'author': 'HashMicro/GYB IT Solutions- Kunal/Goutham',
    'version': '1.0',
    'description': 'User can add Qr code image for payment',
    'website': 'http://www.hashmicro.com',
    'category': 'Expense',
    'summary': 'Payment QR Code',
    'depends': ['account', ],
    'data': [
             'views/qr_code_view.xml',
             'security/ir.model.access.csv',
             'data/data.xml',
            ],
    'installable': True,
    'application': True,
    'auto_install':False,
}
