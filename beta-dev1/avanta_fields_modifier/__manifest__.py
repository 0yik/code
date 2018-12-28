# -*- coding: utf-8 -*-
{
    "name": "Avanta Fields Modifier",
    "author": "HashMicro/Axcensa",
    "version": "10.0.1.0",
    "website": "www.hashmicro.com",
    "category": "Sales and Lead Management",
    "depends": ['sale','crm', 'sale_crm','stock'],
    "data": [
        "data/crm_state_data.xml",
        "data/ehl_renewal_email_template.xml",
        "data/lead_allocation_email_template.xml",
        "data/module_data.xml",
        "data/menu_name.sql",
        "data/ir_cron_data.xml",
        "security/sales_team_security.xml",
        "security/ir.model.access.csv",
        "report/proposal_template_view.xml",
        "report/report.xml",
        "views/avanta_fields_modifier_view.xml",
        "views/avanta_sale_crm_views.xml",
        "wizard/crm_lead_won_view.xml",
        "views/crm_lead_views.xml",
        "views/in_progress_views.xml",
        "views/invoice_view.xml",
        "views/res_partner_views.xml",
        "views/crm_lead_queue.xml",
        "wizard/crm_lead_lost_view.xml",
        "wizard/import_products_view.xml",
        "wizard/lead_import_view.xml",

    ],
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}