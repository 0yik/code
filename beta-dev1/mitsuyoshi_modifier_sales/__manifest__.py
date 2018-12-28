# -*- coding: utf-8 -*-
{
    'name': "Mitsuyoshi Modifier Sale",
    'summary': """
        Modify tree view table in Quotation and Sales Order
    """,
    'description': """
        Modify tree view table in Quotation and Sales Order
    """,
    'author': "HashMicro/Quy",
    'website': "http://www.hashmicro.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['sale','so_blanket_order'
                ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}