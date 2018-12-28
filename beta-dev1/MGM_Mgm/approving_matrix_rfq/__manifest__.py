# -*- coding: utf-8 -*-
{
    'name': "Approving Matrix RFQ",


    'description': """
        Allow users to select the approving user based on the selected Amount range.
    """,

    'author': "HashMicro/Mp Technolabs/ Vatsal",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['approving_matrix_configuration','purchase','mail',],

    # always loaded
    'data': [
        'views/purchase_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}