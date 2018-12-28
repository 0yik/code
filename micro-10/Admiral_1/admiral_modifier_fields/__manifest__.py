# -*- coding: utf-8 -*-
{
    'name': "admiral_modifier_fields",

    'summary': """ """,

    'description': """
    """,

    'author': "HashMicro / Sang, Tri Nguyen",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HashMicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'account', 'purchase', 'stock', 'barcode_weighing_interface'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/admiral_modifier_view.xml',
        'views/stock_product_lot_views.xml',
        'views/product_template_views.xml',
        'views/mrp_workcenter_views.xml',
        'report/invoice_template.xml',
        'report/proforma_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}