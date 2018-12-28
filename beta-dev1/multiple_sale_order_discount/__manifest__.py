{
    'name': 'Multiple Discount on Sale Order',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 6,
    'summary': "Discount on Sale order  Amount ",
    'author': 'mohamed.sharaf.mo@gmail.com',
    'company': 'mohamedmoka93',
    'website': "https://eg.linkedin.com/in/mohamedsharafmo",
    'description': """

Sale Discount for Total Amount
=======================
Module to manage discount on total amount in Sale Order.
        as an specific amount or percentage
""",
    'depends': ['base', 'sale'],
    'data': [
        'views/sale_order_view.xml',
        'views/sale_report.xml',

    ],
    'demo': [
    ],
    'price': '25',
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
