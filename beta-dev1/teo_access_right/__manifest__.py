{
    'name': 'Teo Garment Access Right',
    'description': 'Teo Garment Access Right for Sale, Purchase, Employee, Expense, Leave, Attendance,  Payroll, Customer Invoice, Vender bills, Credit Note, Debit Note, Receipt & Payment, Advisory & Reports modules.',
    'category': 'AccessRight',
    'version': '1.0',
    'author': 'HashMicro / Janbaz Aga',
    'website': 'www.hashmicro.com',
    'depends': ['base','sale','purchase','hr','account','modifier_teo_purchase_order'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/purchase_view.xml',
    ],
    'qweb': [
        ],
    'application': True,
    'installable': True,
}
