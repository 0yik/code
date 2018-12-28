{
    'name': 'POS Product Name / Variant',
    'category': 'point of sale',
    'summary': 'POS Product Name',
    'version': '1.4',
    'description': """
        POS Product Name
        """,
    'author': 'Hashmicro / MpTechnolabs - Bipin Prajapati',
    'website': 'www.hashmicro.com',
    'depends': ['pos_base', 'sale', 'pos_combo'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos_combo.xml',
    ],
    'installable': True,
    'application': True,
}
