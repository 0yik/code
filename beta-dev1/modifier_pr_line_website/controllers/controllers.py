# -*- coding: utf-8 -*-
from odoo import http
from werkzeug import url_encode
import werkzeug

class PurchaseRequestLine(http.Controller):
    @http.route('/purchase_request_line', type='http', auth='public', website=True)
    def purchase_request_line(self, **kw):
        params = dict(view_type='list')
        action = http.request.env.ref('purchase_request.purchase_request_line_form_action')
        if action:
            params['action'] = action.id
        else:
            params['model'] = 'purchase.request.line'

        print "\n-", url_encode(params), """- urlencode(params) -"""
        return werkzeug.utils.redirect('/web?#%s' % url_encode(params))
