# -*- coding: utf-8 -*-
import base64
import mimetypes

from odoo import api, http, _
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition


class WebsiteDemo(http.Controller):

    @http.route('/otp/download/<int:queue>', type='http', auth="public", website=True, csrf=False)
    def opt_download_index(self, queue, **kw):
        # Send email
        # Step1: Call send email
        queue = request.env['otp.link.queue'].browse(queue)
        queue.sudo().send_email()

        return http.request.render('hm_otp_email.object', {
            'object': queue,
            'show_invalid': False,
        })

    @http.route('/otp/verify/', auth='public', csrf=False)
    def opt_download_verify(self, id, token, **kw):
        queue_obj = request.env.get('otp.link.queue')
        queue = queue_obj.browse(int(id))
        if queue.verify_token(token):
            if queue:
                result = queue.sudo().download_attachment()
                if result:
                    filecontent = base64.b64decode(result.get('base64'))
                    filename = result.get('filename')
                    content_type = mimetypes.guess_type(filename)
                    if filecontent and filename:
                        return request.make_response(
                            filecontent,
                            headers=[('Content-Type', content_type[0] or 'application/octet-stream'),
                                     ('Content-Disposition', content_disposition(filename))])
        else:
            queue.sudo().send_email()

            return http.request.render('hm_otp_email.object', {
                'object': queue,
                'show_invalid': True,
            })