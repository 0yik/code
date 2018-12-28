{
    'name': 'POS Product Price',
    'category': 'point of sale',
    'summary': 'POS Product Price',
    'version': '1.0',
    'description': """
        POS Product Price
        1. Remove Picture of product
        2. Show only product name and product price 
        """,
    'author': 'Hashmicro / MpTechnolabs - Bipin Prajapati',
    'website': 'www.hashmicro.com',
    'depends': ['point_of_sale'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos_combo.xml',
    ],
    'installable': True,
    'application': True,
}
