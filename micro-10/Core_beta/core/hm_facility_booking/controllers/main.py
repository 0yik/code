# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, datetime

import pytz
from odoo import http
from odoo.addons.website_portal.controllers.main import website_account
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

DEFAULT_FRONTEND_DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
LIST_STATES = {
    'draft': 'Draft',
    'confirm': 'Confirmed',
    'cancel': 'Canceling',
}

class website_account(website_account):

    @http.route(['/my/facility/booking'], type='http', auth="user", website=True)
    def my_facility_booking(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({'location': request.env['location'].sudo().search([]),
                       'facility': request.env['maintenance.equipment'].sudo().search([('required_booking', '=', True)])}
                      )
        return request.render("hm_facility_booking.portal_my_fbo", values)

    @http.route(['/facility/submit/booking'], type='http', auth="user", website=True, csrf=False)
    def my_facility_submit_booking(self, **kw):
        values = self._prepare_portal_layout_values()
        booking_start_date = kw.get('booking_start_date')
        booking_end_date = kw.get('booking_end_date')
        booking_start_date = self.convert_tz_to_utz(booking_start_date).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        booking_end_date = self.convert_tz_to_utz(booking_end_date).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        check_overlapped = request.env['facility.booking'].check_overlapped_booking(kw.get('facility'),booking_start_date,
                                                                                    booking_end_date)
        if check_overlapped:
            values.update({
                'booking_start_date' : datetime.strptime(kw.get('booking_start_date'), DEFAULT_FRONTEND_DATETIME_FORMAT).strftime("%d/%m/%Y %H:%M:%S"),
                'booking_end_date' : datetime.strptime(kw.get('booking_end_date'), DEFAULT_FRONTEND_DATETIME_FORMAT).strftime("%d/%m/%Y %H:%M:%S"),
            })
            return request.render("hm_facility_booking.portal_fbo_submit_fail", values)
        else:
            vals = {
                'tenant_id': values.get('user').partner_id.id,
                'street': values.get('user').partner_id.street,
                'phone': values.get('user').partner_id.phone,
                'mobile': values.get('user').partner_id.mobile,
                'email': values.get('user').partner_id.email,
                'location_id': kw.get('location'),
                'facility_id': kw.get('facility'),
                'booking_start_date': self.convert_tz_to_utz(kw.get('booking_start_date')),
                'booking_end_date': self.convert_tz_to_utz(kw.get('booking_end_date')),
                'state' :   'confirm',
            }
            request.env['facility.booking'].sudo().create(vals)

            return request.render("hm_facility_booking.portal_fbo_submit", values)

    def get_timezone_diff(self, date):
        my_tz = pytz.timezone(request._context.get('tz') or 'UTC')
        date = my_tz.localize(date)
        date.replace(tzinfo=my_tz)
        return date.strftime('%z')

    def convert_utz_to_tz(self, date):
        date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_diff = self.get_timezone_diff(date)
        if tz_diff[0] == '-':
            date = date - timedelta(hours=int(tz_diff[1:3]), minutes=int(tz_diff[3:]))
        else:
            date = date + timedelta(hours=int(tz_diff[1:3]), minutes=int(tz_diff[3:]))
        return date

    def convert_tz_to_utz(self, date):
        date = datetime.strptime(date, DEFAULT_FRONTEND_DATETIME_FORMAT)
        tz_diff = self.get_timezone_diff(date)
        if tz_diff[0] == '-':
            date = date + timedelta(hours=int(tz_diff[1:3]), minutes=int(tz_diff[3:]))
        else:
            date = date - timedelta(hours=int(tz_diff[1:3]), minutes=int(tz_diff[3:]))
        return date

    @http.route(['/my/fbo/tree'], type='http', auth="user", website=True)
    def my_facility_booking_order_tree(self, **kw):
        values = self._prepare_portal_layout_values()
        offset = 0
        show_page = True
        if kw.get('page', False):
            offset = 0
        fbos = request.env['facility.booking'].sudo().search([('tenant_id', '=', values.get('user').partner_id.id)],
                                                             offset=offset, limit=10)
        if len(fbos) <= 10:
            show_page = False
        fbo_es = []
        for fbo in fbos:
            fbo_es.append({
                'name': fbo.facility_id.name,
                'booking_start_date': self.convert_utz_to_tz(fbo.booking_start_date).strftime("%d/%m/%Y %H:%M:%S"),
                'booking_end_date': self.convert_utz_to_tz(fbo.booking_end_date).strftime("%d/%m/%Y %H:%M:%S"),
                'state': LIST_STATES[fbo.state],
            })
        values.update({'fbo_es': fbo_es,
                       'offset': offset,
                       'show_page': show_page,
                       })
        return request.render("hm_facility_booking.portal_my_booking_facility_order_tree", values)

# class CheckValidateFacilityBooking(http.Controller):
#
#     @http.route(['/facility/validator'], auth='public', csrf=False)
#     def vat_validator(self, **post):
#         website_account_obj = website_account()
#         booking_start_date = post['booking_start_date']
#         booking_end_date = post['booking_end_date']
#         booking_start_date = website_account_obj.convert_tz_to_utz(booking_start_date).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#         booking_end_date = website_account_obj.convert_tz_to_utz(booking_end_date).strftime(DEFAULT_FRONTEND_DATETIME_FORMAT)
#         check_overlapped = request.env['facility.booking'].check_overlapped_booking(booking_start_date,
#                                                                                      booking_end_date)
#         if check_overlapped:
#             return True
#         else:
#             values = {
#                 'sales_rep' : False,
#                 'company' : request.env.user.company_id,
#                 'user' : request.env.user
#             }
#             partner = request.env.user.commercial_partner_id
#             vals = {
#                 'tenant_id': partner.id,
#                 'street': partner.street,
#                 'phone': partner.phone,
#                 'mobile': partner.mobile,
#                 'email': partner.email,
#                 'location_id': post.get('location'),
#                 'facility_id': post.get('facility'),
#                 'booking_start_date': website_account_obj.convert_tz_to_utz(post.get('booking_start_date')),
#                 'booking_end_date': website_account_obj.convert_tz_to_utz(post.get('booking_end_date')),
#             }
#             request.env['facility.booking'].sudo().create(vals).action_facility_confirm()
#             return request.render("hm_facility_booking.portal_fbo_submit",values)