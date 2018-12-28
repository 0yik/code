{
    'name': 'Sale Order Website',
    'author': 'HashMicro / Quy',
    'category': 'Website',
    'description': 'Make SO Online',
    'version': '1.0',
    'depends': ['sale', 'website', 'purchase'],
    'data': [
        'security/group_access.xml',
        # 'security/ir.model.access.csv',
        'data/so_website_menu.xml',
        'views/templates.xml',
    ],
    "installable": True,
    "auto_install": False,
}