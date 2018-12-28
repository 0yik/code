# -*- coding: utf-8 -*-
{
    'name': "dzh_sales_pipeline_retail_report_modify",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Luc",
    'website': "vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','report','dzh_modifier_fields'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/dzh_sales_pipeline_retail_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}