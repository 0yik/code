# -*- coding: utf-8 -*-
{
    'name': "absolutepiano_modifer_customer",

    'description': """
        modifer customer company absolutepiano
    """,

    'author': "HashMicro/Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'absolutepiano_reusable_poscustomer'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}