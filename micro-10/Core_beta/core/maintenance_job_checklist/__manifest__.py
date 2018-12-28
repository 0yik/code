# -*- coding: utf-8 -*-
{
    'name': "maintenance_job_checklist",

    'summary': """
        Allow users to create a template checklist for each type of jobs""",

    'description': """
    """,

    'author': "HashMicro / Duy",
    'website': "www.hashmicro.com",
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base','maintenance','stable_account_analytic_analysis','maintenance_job_order','maintenance_invoice'
    ],

    # always loaded
    'data': [
        'views/job_checklist_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}