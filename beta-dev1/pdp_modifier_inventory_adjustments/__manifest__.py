# -*- coding: utf-8 -*-

{
    'name': 'PDP Modifier Inventory Adjustment',
    'version': '1.0',
    'summary': 'Modify form and Inventory Details table in Inventory Adjustments own by PDP',
    'description': """
        Modify form and Inventory Details table in Inventory Adjustments own by PDP
    """,
    'author': 'HashMicro / Quy',
    'website': 'www.hashmicro.com',
    'category': 'stock',
    'depends': ['stock','pdp_modifier_inventory_reordering_rules'],
    'demo': [],
    'data': [
        'views/inventory_adjustment.xml',
        'views/import_product_line.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
