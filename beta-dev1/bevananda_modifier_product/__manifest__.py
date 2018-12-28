# -*- coding: utf-8 -*-
{
    'name': "bevananda_modifier_product",

    'summary': """
        to add new textfield in products own by Bevananda""",

    'description': """
        to add new textfield in products own by Bevananda
    """,

    'author': "Rajnish",
    'website': "http://www.linescripts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}