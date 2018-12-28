{
    'name': 'Asset Movement',
    'summary': '',
    'description': 'Allows user to submit Asset Request and upon approval to record in the corresponding Assets as well as showing history of Asset Movements.',
    'category': 'Accounting',
    'version': '1.0',
    'author': 'HashMicro / Mareeswaran',
    'website': 'www.hashmicro.com',
    'depends': [
        'account_asset', 'asset_fix',
    ],
    'data': [
        'data/data.xml',
        'views/account_asset_view.xml',
        'views/account_asset_request_view.xml',
        'views/account_asset_movement.xml',
    ],
    'application': True,
    'installable': True,
}