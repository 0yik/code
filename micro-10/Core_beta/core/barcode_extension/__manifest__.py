# -*- coding: utf-8 -*-
{
    'name': "barcode_extension",

    'description': """
            1. The following applies to all types of operations; “Receipts” and “Delivery Orders” and “Internal Transfers”
                a. In screen no 3, if the barcode detected is another product, close the popup and add the line in the DO. If the new product scanned is also “By Lots” or “By Serial Number”, popup screen 3 for this products’ serial numbers
                2. In inventory adjustments:
                a. When I scanned Serial number, it should be able to search the serial number and product
                3. For Delivery Order Out and Internal Transfer:
                a. If the barcode scanned is a serial number, the line is added on the DO straightaway
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'barcodes', 'stock_barcode'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}