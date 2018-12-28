{
    'name': 'Modifier Employee Late',
    'author': 'HashMicro / Quy',
    'category': 'Employee',
    'description': 'Employee',
    'version': '1.0',
    'depends': ['hr_payroll',],
    'data': [
        # 'security/group_access.xml',
        # 'security/ir.model.access.csv',
        'views/employee_late.xml'
    ],
    "installable": True,
    "auto_install": False,
}