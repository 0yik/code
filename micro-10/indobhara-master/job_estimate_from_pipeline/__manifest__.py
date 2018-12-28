# -*- coding: utf-8 -*-
{
    'name': 'Job Estimate from Pipeline',
    'version': '1.0',
    'category': 'Job Estimate',
    'author': 'HashMicro/ JanbazAga',
    'website': "http://www.hashmicro.com",
    'summary': 'Can set margin on job estimate and create quotation based on margin.',
    'depends': [
        'job_cost_estimate_customer','crm'
    ],
    'data': [
        'views/crm_lead_view.xml',
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
