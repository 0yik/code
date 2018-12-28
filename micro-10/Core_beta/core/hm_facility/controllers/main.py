# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo import tools
from odoo.tools.translate import _

from odoo.fields import Date
from odoo.addons.website_portal.controllers.main import website_account

class website_account(website_account):

    @http.route(['/my/helpdesk/ticket'], type='http', auth="user", website=True)
    def my_helpdesk_ticket(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({'location': request.env['location'].sudo().search([]),
                       'facility': request.env['maintenance.equipment'].sudo().search([]),
                       'ticket_type': request.env['helpdesk.ticket.type'].sudo().search([])})
        return request.render("hm_facility.portal_my_helpdesk", values)

    @http.route(['/helpdesk/submit/ticket'], type='http', auth="user", website=True, csrf=False)
    def my_helpdesk_submit_ticket(self, **kw):
        values = self._prepare_portal_layout_values()
        vals={'name': kw.get('tsubject'),
              'partner_id':values.get('user').partner_id.id,
              'partner_email': values.get('user').partner_id.email,
              'ticket_type_id': kw.get('ttype'),
              'location_id': kw.get('location'),
              'facility_id': kw.get('facility')}
        request.env['helpdesk.ticket'].sudo().create(vals)
        return request.render("hm_facility.portal_ticket_submit", values)
