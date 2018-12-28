{
    'name':"Modifier TGW Contract",
    'summary': """Manage the Product Booking""",
    'description': 'To explain how to manage the Contract linked to The Gown Warehouse.',
    'author': "HashMicro / Inkal",
    'website':"http://www.hashmicro.com",
    'depends': [ 'project_milestone','product_booking_contract','hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/data_view.xml',
        'wizard/contract_terms_and_conditions_wizard.xml',
        'views/contract_view.xml',
        'views/milestone_contract_booking_view.xml',
    ],
    'category': 'Booking',
    'version':'1.0',
    'application': True,
}
