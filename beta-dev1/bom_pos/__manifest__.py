{
    'name': 'Hashmicro Bom POS',
    'description': 'This module intends to have functionality to reduce bill of materials in inventory when “Done” button is clicked in Kitchen view',
    'category': 'Stock',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs / chankya',
    'website': 'www.hashmicro.com',
    'depends': ['point_of_sale'],
    'data': [
        'data/product_data.xml',
        'views/kitchen_template_view.xml'
    ],
    'application': True,
    'installable': True,
    'qweb': [
    ]
}
