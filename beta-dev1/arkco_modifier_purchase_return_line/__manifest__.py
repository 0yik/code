# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier Purchase Return Line",

    'summary': """
        To create a pending status if the purchase order has cancelled""",

    'description': """
    """,

    'author': "Teksys Enterprises",
    'website': "http://www.yourcompany.com",
    'category': 'Purchase',
    'version': '1.1',

    'depends': ['base', 'purchase', 'approving_matrix_rfq'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/edit_close.xml',
    ],
}
