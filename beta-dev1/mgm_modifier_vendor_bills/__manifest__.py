{
    'name': 'mgm_modifier_vendor_bills',
    'author': 'HashMicro / Duy',
    'category': 'Invoice',
    'description': 'To modify field in Vendor Bills own by MGM',
    'version': '1.0',
    'depends': ['account','account_asset','mgm_modifier_purchase'],
    'data': [
        'views/account_invoice.xml',
    ],
    "installable": True,
    "auto_install": False,
}