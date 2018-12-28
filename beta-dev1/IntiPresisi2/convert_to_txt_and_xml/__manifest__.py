{
    'name': ' Convert to .txt and .xml',
    'category': 'report',
    'summary': 'Export Customer, Product and Sale Order',
    'version': '1.0',
    'author': 'HashMicro / Kunal',
    'website': 'www.hashmicro.com',
    'description': """
Features:
=========
    1.Convert to .xml    
    
      - Sales Order
        
        - Create a button in list Form View "Export to XML"
        
        - Client able to chose which SO convert to XML
               
      - Quotation
              
        - Create a button in list Form View "Export to XML"
        
        - Client able to chose which Quotation convert to XML
        
    2.Convert to .txt    
    
      - Customer
               
        - Create a button in list Form View "Export to Txt"
        
        - Client able to chose which Customer convert to Txt        
        
      - Product
               
        - Create a button in list Form View "Export to Txt"
        
        - Client able to chose which Product convert to Txt
        
        """,
    'depends': [
                'product_quotation_customize',
                'quotation_pit_extended_ten',
    ],
    'data': [
            "wizard/export_product_wizard.xml",
            "wizard/export_customer_wizard.xml",
            "wizard/export_so_wizard.xml",
            "views/convert_to_xml_view.xml",         
    ],
    'installable': True,
    
}
