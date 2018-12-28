{
    # Theme information
    'name' : 'Theme Honos',
    'category' : 'Theme/eCommerce',
    'version' : '1.0',
    'summary': 'Fully Responsive Odoo eCommerce Theme for Fashion',
    'description': """""",

    # Dependencies
    'depends': [
            #'website',
             'honos_attribute_filter',
             'honos_latest_blogs',
             'honos_brand',
             'honos_category',
             'honos_category_attribute',
             'honos_category_description',
             'honos_404',
             'honos_extra_features',
             'honos_recently_viewed',
             'honos_cms_blocks',
             'honos_contact',
             #'honos_email_subscriber',
             'honos_layout1',
             'honos_layout2',
             'honos_layout3',
             'honos_reset_password',
             'honos_shop_left_sidebar',
             'honos_shop_list',
             'honos_shop_right_sidebar',
             'honos_signin',
             'honos_signup',
             'honos_similar_product',
             'honos_product_carousel_wishlist',
             'honos_quick_view_compare',
             'honos_quick_view_wishlist',
             'honos_carousel_quick_view',
             'honos_pricefilter',
             'honos_customize_theme',
             'honos_compare_wishlist',
                  
    ],


    # Views
    'data': [
          'data/honos_data.xml',  
          'data/company_data/company_data.xml',
    ],
   
    #Odoo Store Specific
    'live_test_url': 'http://honos.themedemo.emiprotechnologies.com',
    'images': ['static/description/image.jpg'],
    
    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'http://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Technical
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 199.00,
    'currency': 'EUR',
}
