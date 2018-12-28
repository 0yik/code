# -*- coding: utf-8 -*-
{
    'name': "warehouse_serializer_mrp",

    'summary': """
        Serialize Product on MO""",

    'description': """
        Auto generate serial/lot number of Product on MO
    """,

    'author': "HashMicro / Hoang",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mrp',
        'warehouse_serializer',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
        'views/serial_lot_number.xml',
        'views/qr_code_views.xml',
    ],
    # only loaded in demonstration mode
}