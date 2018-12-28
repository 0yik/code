# -*- coding: utf-8 -*-

import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request


class MassMailController(http.Controller):

    @http.route('/r/<string:code>/m/<int:stat_id>', type='http', auth="none")
    def full_url_redirect(self, code, stat_id, **post):
        country_code = request.session.get('geoip', False) and request.session.geoip.get('country_code', False)
        print code, stat_id
        request.env['link.tracker.click'].add_click(code, request.httprequest.remote_addr, country_code, stat_id=stat_id)
        return werkzeug.utils.redirect(request.env['link.tracker'].get_url_from_code(code), 301)

