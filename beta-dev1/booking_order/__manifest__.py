# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Booking Order',
    'version' : '1.1',
    

    'category': 'sale',
    'website': 'sahilnavadiya005@gmail.com',
    'depends' : ['sale', 'product','calendar','stock','mrp','hr'],
    'data': [
        'views/booking_team.xml',
        'views/booking_order.xml',
        'views/work_order.xml',   
        'views/team.xml',
        'views/product.xml',
        'views/calendar.xml',
	    'views/sale_order.xml',
        'views/employee.xml',
        'views/stock_production_lot.xml',
        'views/sale_order_setting.xml',
        'security/view_group.xml',
        'security/ir.model.access.csv',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
   
}
