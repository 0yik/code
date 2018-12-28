# -*- coding: utf-8 -*-
{
    'name': 'Asset Fix',
    'version': '1.0',
    'category': 'Asset Management',
    'sequence': 10,
    'summary': 'setup for asset management journal entry creation',
    'description': "This module includes setup for creation of journal entry from a wizard",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/Saravanakumar',
    'depends': ['account_asset'],
    'data': [
        'views/asset_location_view.xml',
        'views/asset_view.xml',
        'wizard/journal_creation_wizard_view.xml',
        'wizard/asset_revalue_view.xml',
        'report/account_asset_report_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}