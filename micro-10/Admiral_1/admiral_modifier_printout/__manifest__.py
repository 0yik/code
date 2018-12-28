# -*- coding: utf-8 -*-
{
    'name': "admiral_modifier_printout",

    'summary': """ """,

    'description': """
    """,

    'author': "HashMicro / Sang,Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HashMicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'account', 'purchase','stock', 'mrp', 'generate_2d_barcode'],

    # always loaded
    'data': [
        'report/manufacturing_orders.xml',
        'views/product_template_views.xml',
        'report/purchase_order_reports.xml',
        'report/delivery_order_reports.xml',
        'report/packing_list_reports.xml',
        'report/invoice_reports.xml',
        'report/report_to_excels.xml',
        'report/report_to_excels.xml',
        'report/qr_code_views.xml',
        'report/location_barcode.xml',
    ],
    # only loaded in demonstration mode


    'css' : [
        '/admiral_modifier_printout/static/src/css/style.css'
    ]
}