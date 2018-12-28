# -*- coding: utf-8 -*-
{
    'name': "MUMS Purchase Order Layout",

    'summary': """This module is written to over ride the report layouts""",

    'description': """This module is written to over ride the report layouts""",

    'author': "Hashmicro / Vinay",
    'website': "http://www.hashmicro.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report', 'purchase', 'amazon_sqs_connector'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/report_paperformat_data.xml',
        'report/report_layout.xml',
        'report/report_purchase_order.xml',

    ],
}