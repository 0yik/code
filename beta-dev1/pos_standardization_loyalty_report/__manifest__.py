{
    'name' : 'pos_standardization_loyalty_report',
    'version' : '1.0',
    'category': 'pos',
    'author': 'HashMicro',
    'description': """ 
    pos_gross_timing_report(timing_reports + pos_sarangoci_report) + pos_loyalty_reports
    """,
    'website': 'www.hashmicro.com',
    'depends' : ['base','pos_loyalty','pizzahut_loyalty_history','cogs_bom_pos','complex_kds', 'sales_field_city'],
    'data': [
        'views/pos_standardization_loyalty_report.xml'
    ],
    'demo': [
    ],
    'qweb': [
	   'static/src/xml/*.xml',
    ],
}