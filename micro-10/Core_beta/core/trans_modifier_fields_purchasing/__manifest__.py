# -*- coding: utf-8 -*-
{
    'name': "trans_modifier_fields_purchasing",

    'summary': """
        Modify Purchase""",

    'description': """
        modifier_fields_purchasing
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
        'purchase',
        'point_of_sale',
        'hr'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/access_right_group.xml',
        'views/product_template_view.xml',
        'views/approving_matrix_views.xml',
        'views/account_invoice_views.xml',
        'views/purchase_request_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}