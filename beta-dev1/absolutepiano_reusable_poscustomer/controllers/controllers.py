# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class AbsolutepianoModiferPoscustomer(http.Controller):

    @http.route('/web/pos/client_info', auth='public', type='json',)
    def get_client_info(self, **kw):
        singapore = request.env.ref('base.sg')
        country_code = request.env['partner.country.code'].search([('country','=',singapore.id)], limit=1)
        return {
            'country' : [singapore.id, singapore.name],
            'country_code' : [country_code.id, country_code.name] if country_code else False,
        }
