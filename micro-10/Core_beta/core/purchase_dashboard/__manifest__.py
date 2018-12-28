{
    'name': 'Purchase Dashboard',
    'author': "HashMicro / Duy",
    'website': "http://www.hashmicro.com",
    'version': '1.0',
    'description': 'Purchase Dashboard',
    'depends': [
                'purchase',
                'purchase_request',
                'purchase_tender_comparison'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/dashboard_history_scheduler_view.xml',
        # 'views/department_view.xml',
        # 'views/company_view.xml',
        # 'views/hr_view.xml',
        'data/template_view.xml',
        'views/purchase_dashboard.xml',
        # 'views/dashboard_history_view.xml',
    ],
    'qweb': [
        "static/src/xml/purchase_dashboard.xml",
    ],
    'sequence': 1,
    'installable': True,
    'auto_install': False
}
