import json
import base64
import odoo
from odoo import http
from odoo.http import request
from datetime import timedelta, date, datetime



class posKitchen(http.Controller):    
    
    @http.route(['/history'], type='json', auth="public", website=True)
    def history(self, **kwargs):
        values = []
        domain = []
        if kwargs.get('current_screen'):
            domain = [('current_screen', '=', kwargs.get('current_screen'))]
        print "DOMAIN   ",domain
        order_history = request.env['order.history'].sudo().search(domain)
        print "Order history   ",order_history
        for record in order_history:
            values.append({ 'id': record.id,
                            'product': record.order_item_id.name,
                            'user':record.waiter_user_id.name,
                            'table':record.table_no,
                            'order':record.order_no,
                            'status':record.order_status,
                            'start':record.start_time,
                            'end':record.end_time,
                            'duration':record.duration
                        })
        print "\n valuessssssssssss", values
        return values

