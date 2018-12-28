# -*- coding: utf-8 -*-
{
    'name': "Hide Purchase Order Quotation",

    'summary': """
        Hide Purchase Order Quotation Menu and Status""",

    'description': """
        Hide Purchase Order Quotation Menu and Status""",

    'author': "Hashmicro / Vinay",
    'website': "http://www.hashmicro.com",

    'category': 'Other',
    'version': '0.1',

    'depends': ['base','purchase'],

    'data': [
        'wizard/product_pack_wizard.xml',
        'views/purchase_order_view.xml',
    ],
}
