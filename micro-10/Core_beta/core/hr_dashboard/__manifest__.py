{
    'name': 'Singapore HR Dashboard',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'category': 'Human Resource',
    'website': "http://www.serpentcs.com",
    'version': '1.0',
    'description': 'Dashboard',
    'depends': [
                'sg_hr_employee',
                'hr_attendance',
#                'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/dashboard_history_scheduler_view.xml',
        'views/department_view.xml',
        'views/company_view.xml',
        'views/hr_view.xml',
        'data/template_view.xml',
        'views/hr_dashboard.xml',
        'views/dashboard_history_view.xml',
    ],
    'qweb': [
        "static/src/xml/hr_dashboard.xml",
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False
}
