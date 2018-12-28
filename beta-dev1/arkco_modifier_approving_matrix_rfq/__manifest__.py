# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier Approving Matrix RFQ",

    'summary': """
        Sets the highest max amount approver to RFQ.
        """,

    'description': """
    """,

    'author': "LineScripts",
    'website': "http://www.linescripts.com",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'approving_matrix_rfq'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}