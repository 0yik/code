# -*- coding: utf-8 -*-
{
    'name': "Pricelist item new Menu",

    'summary': """
        Added new menu for pricelist line display
        """,

    'description': """
        New menu added for the pricelist line display
    """,

    'author': "HashMicro / Krupesh",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale', ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_pricelist_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    #    'demo/demo.xml',
    ],
}
