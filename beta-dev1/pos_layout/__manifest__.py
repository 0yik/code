# -*- coding: utf-8 -*-
{
    'name': "pos_layout",

    'description': """
        Update layout POS.
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
        'point_of_sale',
        'three_interface_pos',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_layout_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}