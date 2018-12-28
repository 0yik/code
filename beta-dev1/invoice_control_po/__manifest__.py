# -*- coding: utf-8 -*-
{
    'name': 'Purchase Invoice Control',
    'version': '1.0',
    'category': 'Purchase',
    'summary': 'Invoice control for purchase order',
    'description': """
    When you order 5 items in PO and you receive > 5 items in the shipment, the invoice will remain 5 items.
    If the user wants to edit the quantity to be bigger than the amount in the PO, prompt an error “You cannot invoice more quantity than your PO”. And don’t change the value back to the same with PO.
    """,
    'author': 'Hashmicro/Saravanakumar',
    'website': 'www.hashmicro.com',
    'depends': ['purchase'],
    'data': [
        # 'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': True,
}