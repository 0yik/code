# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SolumController(http.Controller):

    @http.route(['/get_compnay_name'], type='json', auth='public')
    def get_company_name(self, **kwargs):
        user_id = int(kwargs.get('user_id'))
        user = request.env['res.users'].browse(user_id)
        company_name = user.company_id.name
        return company_name

