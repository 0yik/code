# -*- coding: utf-8 -*-
{
    'name': "pos_exit_table_discard_order",

    
    'description': """
        this module intends to have the functionality of discarding unconfirmed menu if the cashier back to table manu from POS view
    """,

    'author': 'HashMicro / MP technolabs / Prakash',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['pos_restaurant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    
}