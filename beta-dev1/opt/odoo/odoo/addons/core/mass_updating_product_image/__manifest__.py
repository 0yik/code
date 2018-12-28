# -*- coding: utf-8 -*-
{
    'name': "mass_updating_product_image",

    'summary': """
        mass updating product image, which allows user to upload multiple images at one time, and those images are named with
        product name, after upload, then we update the product image""",

    'author': "Hashmicro / MpTechnolabs - Prakash Nanda",
    'website': "http://www.hashmicro.com",

    'category': 'Product',
   
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/product_image_select.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application': True,
}