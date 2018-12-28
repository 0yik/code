# -*- coding: utf-8 -*-
{
    'name': "Export Import SO Line",

    'summary': """
        Export Import Sale Order Line""",

    'description': """
        Export Import Sale Order Line #86241371
        #SEB/201718/101/29056
        #95573578
    """,

    'author': "Hashmicro / Krupesh Laiya",
    'website': "https://www.hashmicro.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'wizard/import_export_sale_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
