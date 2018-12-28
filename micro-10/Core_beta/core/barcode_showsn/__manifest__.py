# -*- coding: utf-8 -*-
{
    'name': "barcode_showsn",

    'description': """
        1.Following features are only for Delivery Orders Out
        2. For all products that are “By Lots” or “By Serial Number”, show the recommended lot numbers in the column (normally have to click and popup).
        Example:
        
        3. Recommended Serial Numbers, shows the recommendation of serial numbers based on FIFO, LIFO, FEFO (Odoo default will show in the popup, we just want to show it in the columns)
        4. Scanned Serial Numbers will show the serial numbers scanned.
    """,

    'author': "HashMicro / Hoang",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'stock_barcode',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_pack_operation_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}