from odoo.http import request
from odoo.addons.pos_bus.controller.pos_controller import *
from odoo import api, http
import logging
_logger = logging.getLogger(__name__)

class Bus(Bus):

    @http.route('/longpolling/pos/branch', type="json", auth="public")
    def send_to_branch(self, message, orders_store={}):
        user_send = request.env['res.users'].sudo().browse(message['user_send_id'])
        _logger.info('Send from: %s' % user_send.login)
        if 'value' in message and 'branch_id' in message['value'] and 'from_branch_id' in message['value']:
            branch_id = message['value']['branch_id']
            from_branch_id = message['value']['from_branch_id']
            if branch_id != from_branch_id:
                sessions = request.env['pos.session'].sudo().search([
                    ('state', '=', 'opened'),
                    ('branch_id', '=', branch_id),
                    ('user_id', '!=', user_send.id),
                    ('config_id.screen_type', '=', 'waiter')
                ])
                send = 0
                for session in sessions:
                    _logger.info('Send to users: %s of session %s' % (session.user_id.login, session.id))
                    send += 1
                    request.env['bus.bus'].sendmany([[(request.env.cr.dbname, 'pos.bus', session.user_id.id), message]])
                if send == 0:
                    _logger.info('Empty clients online for sync')
                if message and message.has_key('sequence'):
                    return message['sequence']
                else:
                    return True
        else:
            return False


