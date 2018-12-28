from odoo.http import request
from odoo.addons.pos_bus.controller.pos_controller import *
from odoo import api, http
import logging
_logger = logging.getLogger(__name__)

class Bus(Bus):

    @http.route('/longpolling/pos/bus/branch', type="json", auth="public")
    def send_branch(self, message, orders_store={}):
        user_send = request.env['res.users'].sudo().browse(message['user_send_id'])
        # _logger.info('Send from: %s' % user_send.login)
        # _logger.info('Send message: %s' % message)
        pos_name = message['value'] and message['value'].get('data') and message['value'].get('data').get('name')
        branch = None
        if pos_name:
            order_id= request.env['pos.order'].search([('pos_reference', '=', pos_name)])
            branch = order_id.destination_branch.id
        sessions = request.env['pos.session'].sudo().search([
            ('state', '=', 'opened'),
            ('branch_id', '=', order_id.destination_branch.id),
            ('user_id', '!=', user_send.id)
        ])
        print ">>>>>>>>sessions ",sessions, order_id.destination_branch , user_send
        send = 0
       
       
             # message['value'].get('data') and message['value'].get('data').get('transfer_branch_id')
        for session in sessions:
            print "\t\t\n\t>>>>>>>>>    sendmany   >>>>>>>>>>>>> session senf toooooo bus ", session
            print '---- bus condition ', session, session.config_id, session.config_id.bus_id.id, message['value']['bus_id'] 
            print "---- session.config_id.branch_id.id ======= branch ", session,session.config_id, session.config_id.branch_id.id, branch
            print "--need to flase-- user consition  notttt", user_send.id, session.user_id.id
            if session.config_id.bus_id and branch \
                and session.config_id.bus_id.id != message['value']['bus_id']  \
                and session.config_id.branch_id.id == branch \
                and user_send.id != session.user_id.id:
                

                # _logger.info('\n\n\n-----------Send to: %s and Branch %s' % session.user_id.login, session.config_id.branch_id.name)
                send += 1
                # print "\n\n.... session.config_id.bus_id ",session.config_id.bus_id
                # print ".... branch ",branch
                print "-dddddddddd--- send  -----------Send to "
                request.env['bus.bus'].sendmany(
                    [[(request.env.cr.dbname, 'pos.bus', session.user_id.id), message]])
                print "-request.env.cr.dbname ",request.env.cr.dbname, session
        if send == 0:
            _logger.info('Empty clients online for sync')
        
        if orders_store:
            request.env['pos.bus'].sudo().browse(message['value']['bus_id']).write({
                'orders_store': orders_store
            })
        
        if pos_name:
            order_id.is_order_proceed = True

        if message and message.has_key('sequence'):
            return message['sequence']
        else:
            return True

