{
    # Theme information
    'name' : 'CCM Theme',
    'category' : 'Theme/eCommerce',
    'version' : '1.0',
    'summary': 'Fully Responsive Odoo eCommerce Theme for CCM',
    'description': """""",

    # Dependencies
    'depends': [
            'base',
            'web',
            'website',
            'theme_honos',
			'honos_cart',
			'honos_layout',
			'website_sale',
            'stock',
			'website_animate',
            'product_booking_ccm',
            'point_of_sale',
            'pos_rental',
            'modifier_account_invoice_report',
            'payment_stripe',
            'ccm_website_faq',
    ],


    # Views
    'data': [
          'data/ccm_honos_data.xml',
          'data/company_data/company_data.xml',
          'data/cron_set_rent_discount_on_product.xml',
          'security/ir.model.access.csv',
		  'templates/home_template.xml',
		  'templates/templates.xml',
		  'templates/about_us.xml',
          'templates/custom_made.xml',
          'templates/merchandise.xml',
          'templates/portfolio.xml',
          'templates/site_map.xml',
          'templates/snippets.xml',
          'templates/account.xml',
          'views/product_view.xml',
          'views/website_config_settings_views.xml',
          'views/website_discount_views.xml',
          'report/sale_order_report.xml',
    ],
    # Author
    'author': 'HashMicro / Anand',
    'website': 'http://www.hashmicro.com',

    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
}
