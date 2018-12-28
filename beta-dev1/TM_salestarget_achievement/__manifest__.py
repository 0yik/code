# -*- coding: utf-8 -*-
{
    'name': "TM_salestarget_achievement",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "HashMicro / Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'HashMicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_team', 'crm'],

    # always loaded
    'data': [
        'views/views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}