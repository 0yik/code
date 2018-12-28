# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Marketing Automation",
    'version': "1.0",
    'summary': "Automate Marketing Campaigns",
    'author': "HashMicro/MP Technolabs/Purvi",
    'website': "http://www.hashmicro.com",
    'category': "Marketing",
    'depends': ['mass_mailing'],
    'data': [
        'security/marketing_automation_security.xml',
        'security/ir.model.access.csv',
        'views/marketing_campaign_views.xml',
        'views/marketing_participant_views.xml',
        'views/mail_mass_mailing_views.xml',
        'data/marketing_automation_data.xml',
    ],
    'demo': [],
    'application': True,
}