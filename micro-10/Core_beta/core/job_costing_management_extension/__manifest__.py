# -*- coding: utf-8 -*-
{
    'name': "Job Costing Management Extension",

    'summary': """
        Extension of odoo_job_costing_management module""",

    'description': """
        Extension of odoo_job_costing_management module
    """,

    'author': "Hashmicro/Kuldeep",
    'website': "http://www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', 'odoo_job_costing_management'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'security/estimate_security.xml',
        'report/estimate_report.xml',
        'data/estimate_sequence.xml',
        'data/estimate_mail.xml',
        'views/views.xml',
        'views/sub_contractor.xml',
        'views/templates.xml',
        'views/sale_estimate_views.xml',
        'views/job_type.xml',
    ],

}