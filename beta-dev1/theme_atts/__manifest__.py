# -*- coding: utf-8 -*-
{
    'name': 'Theme ATTS',
    'category': 'Website',
    'summary': "Theme ATTS is a Odoo theme with advanced ecommerce feature, extremely customizable and fully responsive. It's suitable for any e-commerce sites.",
    'version': '10.0.0.1',
    'author': 'HashMicro / Ajay / Bhavik - TechnoSquare',
    'website': 'https://www.hashmicro.com',
    'description': """
Theme ATTS
===================
Theme ATTS is  is a Odoo theme with advanced ecommerce feature, extremely customizable and fully responsive. It's suitable for any e-commerce sites.
        """,
    'depends': ['theme_stoneware', 'document', 'auth_signup', 'atts_class', 'atts_course', 'website_crm'],
    'data': [
        'data/atts_data.xml',
        'data/atts_signup_email.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/registration_view.xml',
        'views/student_view.xml',
        'views/crm_lead_view.xml',
        'views/assets.xml',
        'views/snippets.xml',
        'views/customize_template.xml',
        'views/website_login_register.xml',
        'views/website_layout.xml',
        'views/website_homepage.xml',
        'views/website_contact_us.xml',
        'views/website_funding_claim.xml',
        'views/website_find_course.xml',
        'views/website_mission_vision.xml',
        'views/website_our_profile.xml',
        'views/website_our_partners.xml',
        'views/website_course_registration.xml',
        'views/website_search_certificate.xml',
        'views/report_course_calendar.xml',
        'views/website_corporate_access.xml',
        'views/website_individual_access.xml',
    ],    
    'images': [
    ],
    'installable': True,
}
