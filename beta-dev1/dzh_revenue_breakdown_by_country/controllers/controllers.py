# -*- coding: utf-8 -*-
from odoo import http

# class DzhRevenueBreakdownByCountry(http.Controller):
#     @http.route('/dzh_revenue_breakdown_by_country/dzh_revenue_breakdown_by_country/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dzh_revenue_breakdown_by_country/dzh_revenue_breakdown_by_country/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dzh_revenue_breakdown_by_country.listing', {
#             'root': '/dzh_revenue_breakdown_by_country/dzh_revenue_breakdown_by_country',
#             'objects': http.request.env['dzh_revenue_breakdown_by_country.dzh_revenue_breakdown_by_country'].search([]),
#         })

#     @http.route('/dzh_revenue_breakdown_by_country/dzh_revenue_breakdown_by_country/objects/<model("dzh_revenue_breakdown_by_country.dzh_revenue_breakdown_by_country"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dzh_revenue_breakdown_by_country.object', {
#             'object': obj
#         })