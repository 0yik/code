# -*- coding: utf-8 -*-
{
    'name': "Job Estimate Margin",

    'summary': """
        Can set margin on job estimate and create quotation based on margin.
        """,

    'description': """
        Can set margin on job estimate and create quotation based on margin.
    """,

    'author': "Hashmicro / Mustufa",
    'website': "https://www.hashmicro.com/",
    'category': 'Login',
    'version': '0.1',
    'depends': ['job_costing_management_extension', 'project'],
    'data': [
        'views/sale_estimate.xml',
    ],
}
