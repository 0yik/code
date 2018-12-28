# -*- coding: utf-8 -*-
{
    'name': "FMD Customer Extended",

    'summary': """
        Extended Customer Form and Tree View
    """,
    'description': """
        
    """,

    'author': "Hashmicro / MpTechnolabs - Bhavin Jethva/ Satya/Prakash/ Bipin Prajapati",

    'website': "www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'base',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','sale','account', 'crm', 'stock', 'project', 'utm', 'mass_mailing', 'sales_team', 'purchase', 'mass_mailing', 'website', 'module_board','field_editor','portal','survey','web_readonly_bypass'],

    # always loaded
    'data': [
        'security/partner_security.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
        'views/report_menu.xml',
        'views/res_partner_sequence.xml',
        'views/res_partner_report.xml',
        'views/res_partner_report_form.xml',
        'views/models_view.xml',
        'views/menu.xml',
        'data/service_used_check.xml',
        'data/sequence.xml',
        'views/max_web_hide_list_view_import_view.xml',
        'views/hide_actions_view.xml',

    ],
    # only loaded in demonstration mode
    'installable': True,
}
