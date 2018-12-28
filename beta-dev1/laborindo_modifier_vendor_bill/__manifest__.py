# -*- coding: utf-8 -*-
{
    'name': "Laborindo Modifier Vendor Bill",

    'description': """
        Vendor Bill
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',

    'category': 'Vendor Bill',
    'version': '1.0',

    'depends': ['account','purchase','vit_efaktur'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/vendor_bill.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}