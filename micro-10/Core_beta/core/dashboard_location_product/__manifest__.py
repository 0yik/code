# -*- coding: utf-8 -*-
{
    'name': 'Location Product Dashboard',
    'version': '1.0',
    'summary': 'Quick actions for location based product display.',
    'category': 'stock',
    'author': 'Hashmicro / Saravankumar',
    'website': 'https://www.hashmicro.com/',
    'description':
    """
Location Product dashboard
==============
* Quick access display products in location
    """,
    'depends': ['stock', 'web_planner'],
    'data': [
        'views/dashboard_views.xml',
        'views/dashboard_templates.xml',
        'data/stock_data.xml',
    ],
    'qweb': ['static/src/xml/stock_dashboard.xml'],
    'auto_install': False,
    'application': True,
}
