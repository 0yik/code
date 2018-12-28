# -*- coding: utf-8 -*-
{
    'name': 'Module Board',
    'version': '1.0',
    'category': 'Module Category',
    'sequence': 5,
    'summary': 'setup for Module installation configuration',
    'description': "This module includes all module installation configuration related setup",
    'website': 'http://www.axcensa.com/',
    'author': 'Axcensa',
    'depends': ['base'],
    'data': [
        'views/module_config_view.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}