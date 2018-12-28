{
    'name': 'MGM Modifer Purchase Menu',
    'version': '1.0',
    'summary': 'MGM Modifer Purchase Menu changes',
    'description': 'Changing the Purchase menu order',
    'author': 'Hashmicro/Muthulakshmi/ Mp Technolabs / Vatsal',
    'website': 'www.hashmicro.com',
    'category': 'Purchase',
    'depends': ['purchase','purchase_tender_comparison','mgm_modifier_purchase_request','mgm_modifier_purchase'],
    'data': [
        'views/purchase_menu_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
