# -*- coding: utf-8 -*-
{
    'name': 'Indonesia SPT',
    'version': '10.0.1.0.0',
    'summary': """Indonesia SPT""",
    'description': """Generate Surat Pemberitahuan (SPT) for Indonesia Income tax.""",
    'author': 'Hashmicro/Janbaz Aga',
    'company': 'Hashmicro',
    'website': 'http://hashmicro.com',
    'category': '',
    'depends': ['hr','sg_hr_employee'],
    'license': 'LGPL-3',
    'data': [
        'wizards/wizard_1721_1.xml',
        'wizards/wizard_1721_3a1.xml',
        'wizards/wizard_1721_3a2.xml',
        'reports/spt_1721_template.xml',
        'reports/report_spt_1721_3a1.xml',
        'reports/report_spt_1721_3a2.xml',
        'reports/report.xml',
        'views/indonesia_spt_view.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

