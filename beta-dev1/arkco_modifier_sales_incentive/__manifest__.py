# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier Sales Incentive",

    'summary': """
        """,

    'description': """

    """,

    'author': "LineScripts",
    'website': "http://www.linescripts.com",
    'category': 'Sales',
    'version': '0.1',

    'depends': ['base', 'sale', 'arkco_modifier_sale_commission_target_gt'],

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