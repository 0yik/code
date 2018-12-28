# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.website.models.website import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError
from odoo.addons.website_form.controllers.main import WebsiteForm

_logger = logging.getLogger(__name__)

class EmenuSale(http.Controller):
    
    @http.route(['/shop/eorder'], type='http', auth="public", website=True)
    def eorder(self, customer=None, **post):
        print "\n customerrrrrrrrrrrrrrrrrrr", customer
        order = request.website.sale_get_order()
        user_id = request.env['res.users'].search([('partner_id', '=', order.partner_id.id)])
        pos_session = request.env['pos.session'].search([('user_id', '=', user_id.id),('state','=','opened')], limit=1)
        pos_session_id = pos_session.id
        pos_config_id = pos_session.config_id
        bus_id = request.env['pos.config'].search([('id', '=', pos_config_id.id)]).bus_id.id
        
        pos_session_final = {
                    'bus_id': bus_id,
                    'pos': { 'id': pos_config_id.id, 'name': pos_config_id.name },
                    'user': { 'id': user_id.id, 'name': user_id.name },
        }
        print "\n pos session finalllllll", pos_session_final
        orders_store = []
            
            
        all_lines = []
        for oline in order.order_line:
            lines = {
                'attribute': [],
                'cancel_manager': None,
                'discount': 0,
                'id': oline.id,
                'line_qty_returned': 0,
                'mp_dirty': None,
                'mp_skip': None,
                'next_screen': None,
                'note': "",
                'order_uid': order.name,
                'original_line_id': None,
                'pack_lot_ids': [],
                'popup_option': None,
                'price_unit': oline.price_unit,
                'product_id': oline.product_id.id,
                'qty': oline.product_uom_qty,
                'reward_id': None,
                'session_info': {'created':pos_session_final},
                'state': "Need-to-confirm",
                'summary_screen': None,
                'takeaway_screen': None,
                'tax_ids':[],
                'uid': order.name + '-1',
            }
            all_lines.append([0,0,lines])

        export_data = {
            'amount_paid': 0,
            'amount_return': 0,
            'amount_tax': order.amount_tax,
            'amount_total': order.amount_total,
            'cancelled_lines': [],
            'category': "dive_in",
            'confirmation_time': False,
            'customer_count': 1,
            'dine_is_assign_order': False,
            'emenu_order': True,
            'fiscal_position_id': False,
            'is_return_order': False,
            'is_staff_meal': None,
            'lines': all_lines,
            'statement_ids':[],
            'loyalty_points': 0,
            'multiprint_resume': None,
            'name': order.name,
            'note': None,
            'partner_id': False,
            'payment_plan_id': None,
            'popup_option': "Dine In",
            'pos_session_id': pos_session_id,
            'remove_from_summary': False,
            'return_order_id': False,
            'return_status': "-",
            'reward_id': None,
            'seat_number': 0,
            'sender_branch_id': False,
            'sequence_alphabet': "A",
            'sequence_number': pos_session.sequence_number,
            'session_info': None,
            'temp_customer_name': customer if customer else "",
            'temp_order': False,
            'table_id':False,
            'temporary': False,
            'uid':order.name,
            'user_id': user_id.id
        }

        orders_store.append(export_data)

        values = {
                    'data': export_data,
                    'action': 'new_order',
                    'bus_id': bus_id,
                    'order': export_data,
        }
        
        message = {
                    'user_send_id': user_id.id,
                    'value': values,
        }
        
        user_send = request.env['res.users'].sudo().browse(message['user_send_id'])
        _logger.info('Send from: %s' % user_send.login)
        _logger.info('Send message: %s' % message)
        sessions = request.env['pos.session'].sudo().search([
            ('state', '=', 'opened'),
            ('user_id', '!=', user_send.id)
        ])
        send = 0
        for session in sessions:
            if session.config_id.bus_id and session.config_id.bus_id.id == message['value']['bus_id'] and user_send.id != session.user_id.id:
                _logger.info('Send to: %s' % session.user_id.login)
                send += 1
                request.env['bus.bus'].sendmany([[(request.env.cr.dbname, 'pos.bus', session.user_id.id), message]])
        if send == 0:
            _logger.info('Empty clients online for sync')
        if orders_store:
            res = request.env['pos.bus'].sudo().browse(message['value']['bus_id']).write({
                'orders_store': orders_store
            })
        if res:
            order.sudo().unlink()
            return request.redirect('/shop')
        #if message and message.has_key('sequence'):
            #return message['sequence']
        #else:
            #return True        
