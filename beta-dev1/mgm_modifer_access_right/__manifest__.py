# -*- coding: utf-8 -*-
{
    'name': "mgm_modifer_access_right",
    'summary': """ MGM modifier access right """,
    'description': """ Long description of module's purpose """,
    'author': "Hashmicro/ Luc / MP Technolabs / Vatsal",
    'website': "http://www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mgm_sales_contract','fund_request_b2b','mgm_modifier_purchase_request','utm',
                'purchase_shipping_invoice','mgm_modifier_customer','low_stock_notification',
                'task_list_manager','sg_partner_payment','scheduler_notification','crm_phonecall','mgm_modifier_sales','sales_team'],
    'data': [
        'security/access_right_group.xml',
        'security/ir.model.access.csv',
        'views/mgm_modifier_access_rights_view.xml',
    ],
    'demo': [ ],
}