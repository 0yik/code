{
    'name': 'Sarangoci Access Right',
    'author': 'HashMicro / Quy',
    'category': 'Access Right',
    'description': 'Access Right',
    'version': '1.0',
    'depends': ['sale', 'purchase','account','purchase_request'],
    'data': [
        'security/ir.model.access.csv',
        'views/access_group.xml',
    ],
    "installable": True,
    "auto_install": False,
}