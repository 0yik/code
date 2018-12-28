# -*- coding: utf-8 -*-
{
    'name': "laborindo_invoice_grouping",

    'description': """
       Add filter in invoice and   default filter  on smart button invoice
    """,

    'author': "Hashmicro / MpTechnolabs - Prakash Nanda",
    'website': "http://www.mptechnolabs.com/",
 
    'category': 'sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale','account','laborindo_modifier_invoice_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}