# -*- coding: utf-8 -*-
{
    'name': "Biocare Reports Modifier",

    'summary': """
        Report creation for the biocare""",

    'description': """
        Reporting for biocare project
    """,

    'author': "Hashmicro / Krupesh",
    'website': "https://hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report', 'stock', 'biocare_field_modifier', 'booking_service_V2',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/report_paperformat_data.xml',
        'wizard/export_bo_done_view.xml',
        'wizard/contract_report_custom_view.xml',
        'views/custom_header.xml',
        'views/work_report.xml',
        'views/report_contract.xml',
        'views/report_contract_wizard.xml',
        'views/report_workorder.xml',
        'views/stock_picking_view.xml',
        'views/report_job_sheet.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
