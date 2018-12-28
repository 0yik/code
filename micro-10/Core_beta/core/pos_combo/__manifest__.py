{
    'name': 'POS Combo / Variant',
    'category': 'point of sale',
    'summary': 'Create combo for POS, create multi variants for POS',
    'version': '1.4',
    'price': '100',
    "currency": 'EUR',
    'description': """
        Define one combo (include many product items on 1 combo) for sale \n
        Define multi variants on one product \n
        """,
    'author': 'TL Technology',
    'website': 'https://posodoo.com',
    'depends': ['pos_base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_attribute.xml',
        '__import__/template.xml',
        'view/product.xml',
        'view/pos_order.xml',
        'report/report.xml',
    ],
    'qweb': ['static/src/xml/pos_combo.xml'],
    'installable': True,
    'application': True,
    'support': 'thanhchatvn@gmail.com',
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}
