# -*- coding: utf-8 -*-
{
    'name': "repair_materials",

    'summary': """
        Create a “Repair Materials” check box for Product so that only “repair materials” are shown in the “Product” drop-down list of Repair Orders.""",

    'description': """
        Create a “Repair Materials” check box for Product so that only “repair materials” are shown in the “Product” drop-down list of Repair Orders.
    """,

    'author': "HashMicro",
    'website': "http://www.hasmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'product', 'mrp_repair'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/repair_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}