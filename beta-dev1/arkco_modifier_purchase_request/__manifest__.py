# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier Purchase Request",

    'summary': """
        Removes fiter from Analytic Account field in Products to Purchase Form""",

    'description': """
    """,

    'author': "LineScripts",
    'website': "http://www.linescripts.com",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}