# -*- coding: utf-8 -*-
{
    'name': "Arkco Modifier RFQ Tendor",

    'summary': """
        To set minimum RFQ in a single tender, this module ensures that the purchase 
        tender will not become a PO if the list of Rfq is less than the minimum offer.""",

    'description': """
        
    """,

    'author': "LineScripts",
    'website': "http://www.linescripts.com",

    'category': 'Purchase',
    'version': '1.1',

    'depends': ['base', 'purchase_requisition', 'approving_matrix_rfq'],


    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}