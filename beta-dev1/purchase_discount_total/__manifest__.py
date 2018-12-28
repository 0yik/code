{
    'name': 'Purchase Discount on Total Amount',
    'version': '1.0',
    'category': 'Purchase Management',
    'summary': "Discount on total in Purchase",
    'author': "HashMicro/MP Technolabs/ vatsal",
    'website': "http://www.hashmicro.com",

    'description': """

Purchase Discount for Total Amount
=======================
Module to manage discount on total amount in Purchase.
        as an specific amount or percentage
""",
    'depends': ['purchase','account'],
    'data': [
        'views/purchase_view.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/banner.jpg'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
