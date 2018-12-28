# -*- coding: utf-8 -*-
{
    'name': "barcode_weighing_interface",


    'description': """
        Barcode Scan and Weighing Scale interface for WorkOrders
    """,

    'author': "HashMicro / Vu",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'web', 'bom_routing_management', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/work_order_view.xml',
        'views/barcode_weighing_templates.xml',
    ],
    'qweb' : [
        'static/src/xml/barcode_weighing_scan_interface.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}