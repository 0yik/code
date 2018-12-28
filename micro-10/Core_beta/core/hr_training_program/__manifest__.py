# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Training Programs',
    'version': '1.1',
    'author': 'HashMicro / Ravneet / Vu',
    'category': 'Human Resources',
    'sequence': 75,
    'website': 'www.hashmicro.com',
    'depends': [
        'base_setup',
        'resource',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_training_program_views.xml',
        'wizards/training_requests_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
