{
    'name': "Laborindo Modifier Invoice",

    'description': """
        Timesheet
    """,
    'author': 'HashMicro / Viet',
    'website': 'www.hashmicro.com',

    'category': 'sale,invoice',
    'version': '1.0',

    'depends': ['laborindo_modifier_invoice_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/employee_sequence.xml',
        'views/customer_invoice.xml',
    ],
    # only loaded in demonstration mode
    'qweb': [],
    'demo': [
    ],
}