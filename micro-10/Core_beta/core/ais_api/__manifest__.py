# -*- coding: utf-8 -*-
{
    'name': 'AIS API',
    'version': '1.0',
    'category': 'API',
    'sequence': 15,
    'summary': 'setup for upload IR8A, IR8S and Appendix 8A via API',
    'description': "Integrate EquipERP directly with IRAS’ server via API forAuto-Inclusion Scheme(AIS) submissions of IR8A, IR8S and Appendix 8A.",
    'website': 'http://www.hashmicro.com/',
    'author': 'Hashmicro/ Goutham',
    'depends': [
        'sg_income_tax_report',
        'sg_appendix8a_report'
    ],
    'data': [
        'data/ir_cron_data.xml',
        'views/api_config_view.xml',
        'wizard/ais_api_schedule_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}