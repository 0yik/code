# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web_editor.controllers.main import Web_Editor


class Web_Editor(Web_Editor):


    @http.route(['/mass_mailing/snippets'], type='json', auth="user", website=True)
    def mass_mailing_snippets(self):
        values = {'company_id': request.env['res.users'].browse(request.uid).company_id}
        return request.env.ref('mass_mailing_essentials.s_mail_block_footer_social_left').render(values)
    
    