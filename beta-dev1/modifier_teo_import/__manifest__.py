# -*- coding: utf-8 -*-
{
    'name': 'Modifier TEO Product & Sale Import',
    'version': '1.0',
    'description': """
    """,

    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva",
    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'summary': 'Easy to import Product and Sale Order for TEO Garments.',
    'category' : 'Extra Tools',
    # any module necessary for this one to work correctly
    'depends': ['modifier_teo_sale_order'],
    'data': [
             "views/sale.xml",
#              "views/product_view.xml",
             ],
    'installable': True,
    'application': True,
    'auto_install': False,
}