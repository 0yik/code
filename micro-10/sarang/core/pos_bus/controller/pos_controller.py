from odoo.http import request
from odoo.addons.bus.controllers.main import BusController
from odoo import api, http
import logging
_logger = logging.getLogger(__name__)

class Bus(BusController):

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels = list(channels)
            channels.append((request.db, 'pos.bus', request.uid))
        return super(Bus, self)._poll(dbname, channels, last, options)


    @http.route('/longpolling/pos/bus', type="json", auth="public")
    def send(self, message, orders_store={}):
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
                request.env['bus.bus'].sendmany(
                    [[(request.env.cr.dbname, 'pos.bus', session.user_id.id), message]])
        if send == 0:
            _logger.info('Empty clients online for sync')
        if orders_store:
            request.env['pos.bus'].sudo().browse(message['value']['bus_id']).write({
                'orders_store': orders_store
            })
        if message and message.has_key('sequence'):
            return message['sequence']
        else:
            return True


