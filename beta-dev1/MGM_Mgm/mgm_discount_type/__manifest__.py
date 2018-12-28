{
    'name': 'Modifier Discount Type',
    'category': 'sale',
    'summary': 'Modifier Discount Type',
    'version': '1.0',
    'description': """ Modifier Discount Type """,
    'author': 'Hashmicro / MpTechnolabs / Vatsal',
    'website': 'www.hashmicro.com',
    'depends': ['sale','sale_discount_total','purchase','mgm_modifier_sales'],
    'data': [
        'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
