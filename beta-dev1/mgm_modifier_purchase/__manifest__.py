{
    'name': 'MGM Modifier Purchase',
    'category': 'purchase',
    'summary': 'MGM Modifier Purchase',
    'version': '1.0',
    'description': """
        MGM Modifier Purchase
        """,
    'author': 'Hashmicro / Mareeswaran / MP Technolabs / Vatsal',
    'website': 'www.hashmicro.com',
    'depends': ['account','purchase','account_asset','purchase_requisition','mgm_modifier_purchase_request','purchase_request','mgm_discount_type','puchase_pricelist'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
        'views/purchase_menu.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}
