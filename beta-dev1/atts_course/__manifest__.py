# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'ATTS Course/ School',
    'version': '10.0.1.0.13',
    'author': 'HashMicro / Ajay / Bhavik - TechnoSquare',
    'website': 'https://www.hashmicro.com',
    'images': ['static/description/school.png'],
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For School Management',
    'depends': ['hr', 'crm', 'report'],
    'data': ['security/school_security.xml',
             'security/ir.model.access.csv',
             'wizard/terminate_reason_view.xml',
             'wizard/wiz_send_email_view.xml',
             'views/school_view.xml',
             'data/student_sequence.xml',
             'wizard/assign_roll_no_wizard.xml',
             'wizard/move_standards_view.xml',
             'views/report_view.xml',
             'views/identity_card.xml'],
    # 'demo': ['demo/school_demo.xml'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True
}
