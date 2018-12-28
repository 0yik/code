# -*- coding: utf-8 -*-
{
    'name': "Dzh Sales Pipeline Conference & Education - Report Modify",

    'summary': """
        Sales Revenue Report Reusable""",

    'description': """
    """,

    'author': "Hashmicro ",
    'website': "http://www.hashmicro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hashmicro',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['product','account','report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sales_pipeline_conference_education_report_view.xml',
    ],
}
