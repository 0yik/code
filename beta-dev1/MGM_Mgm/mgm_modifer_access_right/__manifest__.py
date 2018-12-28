# -*- coding: utf-8 -*-
{
    'name': "mgm_modifer_access_right",

    'summary': """
        MGM modifier access right""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Hashmicro/ Luc",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mgm_sales_contract','fund_request_b2b','mgm_modifier_purchase_request','mgm_purchase_multi_analytics','utm',
                'purchase_shipping_invoice','mgm_modifier_customer','low_stock_notification','mgm_contract_multi_analytics','mgm_multi_assign_analytics',
                'task_list_manager','sg_partner_payment','scheduler_notification'],

    # always loaded
    'data': [
        'security/access_right_group.xml',
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}