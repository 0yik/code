{
    'name': 'Modifier Discount Type',
    'category': 'sale,purchase',
    'summary': 'Modifier Discount Type',
    'version': '1.0',
    'description': """
        Modifier Discount Type
        """,
    'author': 'Hashmicro / MpTechnolabs - Vatsal Shah',
    'website': 'www.hashmicro.com',
    'depends': ['purchase','purchase_discount_total','inventory_on_purchase'],
    'data': [
        #'views/sale_view.xml',
        'views/purchase_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
}
