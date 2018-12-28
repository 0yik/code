# -*- coding: utf-8 -*-
{
    'name': "payment_installment",

    'summary': """
        Add function Payment Installment on Sale Order""",

    'description': """
        Add function Payment Installment on Sale Order
    """,

    'author': "HashMicro / Viet",
    'website': "www.hashmicro.com",
    'category': 'Sale',
    'version': '0.1',

    'depends': ['base', 'sale', 'account', 'task_list_manager'],
    # 'installable': False,
    'data': [
        'views/payment_installment_type.xml',
        'views/payment_installment.xml',
        'views/register.xml',
        'views/sale_order.xml',
    ],
}