# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier Sale Commission Target gt",

    'summary': """
        Adds the Sales Team, Start and End Date columns to Commission Form.""",

    'description': """
        
    """,

    'author': "Teksys Enterprises",
    'website': "http://www.yourcompany.com",
    'category': 'Sales',
    'version': '1.1',

    'depends': ['sales_team', 'sale_commission_target_gt'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}