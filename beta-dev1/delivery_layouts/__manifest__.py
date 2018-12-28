# -*- coding: utf-8 -*-
{
    'name': "Delivery layouts",

    'summary': """
        Delivery layouts""",

    'description': """
        Delivery layouts
    """,

    'author': "Hashmicro / Viet",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hashmicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/delivery_order_layout_views.xml',
        'views/packing_list_layout_views.xml',
        'views/product_template_views.xml',
    ]
}