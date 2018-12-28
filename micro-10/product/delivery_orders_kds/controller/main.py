from odoo.http import request
from odoo.addons.pos_bus.controller.pos_controller import *
from odoo import api, http
import logging
_logger = logging.getLogger(__name__)

class Bus(Bus):

    @http.route('/longpolling/pos/branches', type="json", auth="public")
    def sync_with_branch(self, message, orders_store={}):
        user_send = request.env['res.users'].sudo().browse(message['user_send_id'])
        _logger.info('Send from: %s' % user_send.login)
        _logger.info('Send message: %s' % message)
        branch_id = message['value'] and message['value'].get('branch_id')

        sessions = request.env['pos.session'].sudo().search([
            ('state', '=', 'opened'),
            ('branch_id', '=', branch_id),
            ('user_id', '!=', user_send.id),
            ('config_id.screen_type', '=', 'waiter')

        ])
        send = 0
        for session in sessions:
            if session.config_id.bus_id and branch_id:
                _logger.info('Send to: %s' % session.user_id.login)
                send += 1
                request.env['bus.bus'].sendmany(
                    [[(request.env.cr.dbname, 'pos.bus', session.user_id.id), message]])
        if send == 0:
            _logger.info('Empty clients online for sync')

        if message and message.has_key('sequence'):
            return message['sequence']
        else:
            return True

