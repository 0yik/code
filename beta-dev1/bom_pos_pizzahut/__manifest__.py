
{
    'name': 'Bom POS Pizzahut',
    'description': 'This module intends to have functionality to reduce bill of materials in inventory when “Validate” button is clicked in Payment view',
    'category': 'Stock',
    'version': '1.0',
    'author': 'HashMicro / MP Technolabs(chankya)',
    'website': 'www.hashmicro.com',
    'depends': ['staff_meal','mrp'],
    'data': [
        'data/product_data.xml',
        'views/kitchen_template_view.xml'
    ],
    'application': True,
    'installable': True,
    'qweb': [
    ]
}
