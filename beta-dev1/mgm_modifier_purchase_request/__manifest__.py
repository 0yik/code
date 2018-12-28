{
    'name': 'MGM Modifier Purchase Request',
    'category': 'purchase',
    'summary': 'MGM Modifier Purchase Request',
    'version': '1.0',
    'description': """
        MGM Modifier Purchase Request
        """,
    'author': 'Hashmicro / Mareeswaran / MP Technolabs / Vatsal',
    'website': 'www.hashmicro.com',
    'depends': ['purchase_request_to_rfq', 'account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request_view.xml',
        # 'views/ir_cron.xml',
        # 'views/data.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
}
