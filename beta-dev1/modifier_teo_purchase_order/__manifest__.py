# -*- coding: utf-8 -*-
{
    'name': "Modifier TEO Purchase Order",

    'summary': """
        Added fields in Purchase Order Form
    """,
    'description': """
    """,

    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva - Bipin Prajapati",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase','modifier_teo_sale_order'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/purchase_order_view.xml',
        'views/purchase_order_line_view.xml',
        'views/receipt_payment_view.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
}