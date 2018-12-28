{
    'name': "Lead Contract",
    'version': '0.1',
    'category': 'crm',
    'description': """
        1.Contract added to opportunity.
    """,
    'author': "HashMicro / Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",
    'depends': ['sale','crm','sale_crm','calendar','opportunity_partner','stable_account_analytic_analysis'],
    'data': [
        'view/lead_contract_view.xml',        
    ],
    'qweb': [
        # "static/src/xml/sales_name_dashboard.xml",
    ],
}