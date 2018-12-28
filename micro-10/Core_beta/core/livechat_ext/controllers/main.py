# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class LivechatController(http.Controller):

    @http.route('/im_livechat/start_page_done', type="json", auth='public')
    def start_page_done(self, channel_id, name, email):
        channel_obj = request.env["mail.channel"].sudo().browse(channel_id)
        channel_obj.display_start_page = False
        channel_obj.anonymous_name = name
        channel_obj.anonymous_email = email
        if len(channel_obj.name.split(',')) == 2:
            channel_obj.name = name + ',' + channel_obj.name.split(',')[1]
        return True