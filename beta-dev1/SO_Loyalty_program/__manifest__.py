# -*- coding: utf-8 -*-
{
    'name': "SO loyalti program",

   
    'description': """
        This module intends to apply promotion and discount when create sales order.
    """,
    'author': 'HashMicro / MP technolabs - Parikshit Vaghasiya',
    'website': 'www.hashmicro.com',

    'category': 'pos',
    'version': '0.1',

    'depends': ['sale','pos_promotion','pos_promotion_program','product','sales_team','crm','term_of_payment_restrict'],

    # always loaded
    'data': [
        'wizard/promo_line_import_wizard.xml',
        'views/promotion_so_view.xml',
    ],
    # only loaded in demonstration mode
    'qweb':['static/src/xml/*.xml'],
    'demo': [
    ],
}
