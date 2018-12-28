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
    'depends': ['sale','crm','sale_crm','crm_phonecall','calendar','delivery'],
    'data': [
        'security/crm_access_group_enquiry.xml',
        'security/ir.model.access.csv',
        'data/crm_stage_data_v.xml',
        'wizard/lead_ask_code_view.xml',
        'wizard/pricelist_select_by_partner.xml',
        'views/coating_report_view.xml',
        'views/pit_crm_view.xml',
        'views/pit_sale_view.xml',
        'views/quotation_approval_view.xml',        
    ],
    'qweb': [
        "static/src/xml/sales_name_dashboard.xml",
    ],
}