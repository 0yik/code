# -*- coding: utf-8 -*-
{
    'name': 'Asset Maintenance Fleet Link',
    'version': '1.0',
    'category': 'Assets',
    'author': 'HashMicro / MP technolabs / Mital / Saravanakumar',
    'description': 'Asset Maintenance Fleet Link',
    'website': 'www.hashmicro.com',
    'depends': ['base', 'maintenance', 'fleet', 'asset_fix', 'account_asset'],
    'data': [
        'security/ir.model.access.csv',
		'view/account_assets_view.xml',
		'view/fleet_view.xml',
		'view/asset_master_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
