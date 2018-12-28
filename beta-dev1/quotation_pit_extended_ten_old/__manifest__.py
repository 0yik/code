{
    'name': "Quotation Lead Extended",
    'version': '0.1',
    'category': 'crm',
    'description': """
        1. Users can generate quotations and sales orders to an opportunity
        2. There will be a button on the top right of each opportunity to view all the quotations related to him
        3. Instead of "Convert to Quotation", have "Create Quotation" on all opportunity regardless of the kanban status.
        4. Add one button "Convert to Customer" in all Opportunity, which will update the Opportunity status to "Won", and customer record is created
    """,
    'author': "HashMicro / Parikshit Vaghasiya",
    'website': "http://www.hashmicro.com",
    'depends': ['sale','crm','sale_crm'],
    'data': [
        'data/crm_stage_data_v.xml',
        'wizard/lead_ask_code_view.xml',
        'views/pit_crm_view.xml',
    ],
}