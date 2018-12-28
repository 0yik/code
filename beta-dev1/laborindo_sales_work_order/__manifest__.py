# coding=utf-8
{
    'name' : 'Laborindo Sales Work Order Modifier',
    'version' : '1.0',
    'category': 'sale',
    'author': 'HashMicro / TechUltra Solutions / Krutarth Patel',
    'description': """Laborindo Modifier for sales work order
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['sale'],
    'data': [
        'data/sequence_data.xml',
        'views/sales_view.xml',
        'views/work_order_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}