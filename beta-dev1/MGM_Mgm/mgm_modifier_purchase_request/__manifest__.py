{
    'name': 'MGM Modifier Purchase Request',
    'category': 'purchase',
    'summary': 'MGM Modifier Purchase Request',
    'version': '1.0',
    'description': """
        MGM Modifier Purchase Request
        """,
    'author': 'Hashmicro / Mareeswaran',
    'website': 'www.hashmicro.com',
    'depends': ['purchase_request_to_rfq', 'account_asset'],
    'data': [
        'views/purchase_request_view.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
}
