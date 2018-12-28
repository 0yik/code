# -*- coding: utf-8 -*-
{
    'name': "PDP Modifier Sales",
    'summary': """
        Modifier Sales""",
    'description': """
        Modifier Sales
    """,
    'author': "HashMicro / Quy, MPTechnoclabs(Chankya)/ Vatsal",
    'website': "www.hashmicro.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'sale_discount_total','sale_stock','pdp_sales_target_achievement','PDP_modifier_customer','branch',
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/order_line_rows.xml',
        'views/sale_order_view.xml',
        'views/customer_view.xml',
		'views/branch_target.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
