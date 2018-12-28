# -*- coding: utf-8 -*-
{
    'name': 'Helaspice SAP Integration',
    'version': '1.0',
    'category': 'SAP Integration',
    'sequence': 10,
    'summary': 'SAP Integration',
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/ GBS TechnoSoft',
    'depends': ['helaspice_receiving_import'],
    'data': [
        'data/ir_cron_data.xml',
        'views/res_config_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}