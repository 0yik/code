# -*- coding: utf-8 -*-

{
    'name': 'Sales BOM Check',
    'version': '1.0',
    'summary': 'Sales Bill Of Material Check',
    'description': """
        - For the system to have a check on the Product’s Bill of Material (BOM) when confirming the Quotation.
        - System to be able to check on existing Raw Materials quantity and whether the quantity is enough to produce the Product.
        - Auto generate PO when not available
    """,
    'author': 'HashMicro / Kunal',
    'website': 'www.hashmicro.com',
    'category': 'Sale',
    'sequence': 0,
    'images': [],
    'depends': ['sale','mrp','purchase'],
    'demo': [],
    'data': [
        'wizard/sales_bom_check_view.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
