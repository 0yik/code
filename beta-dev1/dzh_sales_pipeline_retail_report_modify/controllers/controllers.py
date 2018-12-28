# -*- coding: utf-8 -*-
from odoo import http

# class DzhSalesPipelineRetailReportModify(http.Controller):
#     @http.route('/dzh_sales_pipeline_retail_report_modify/dzh_sales_pipeline_retail_report_modify/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dzh_sales_pipeline_retail_report_modify/dzh_sales_pipeline_retail_report_modify/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dzh_sales_pipeline_retail_report_modify.listing', {
#             'root': '/dzh_sales_pipeline_retail_report_modify/dzh_sales_pipeline_retail_report_modify',
#             'objects': http.request.env['dzh_sales_pipeline_retail_report_modify.dzh_sales_pipeline_retail_report_modify'].search([]),
#         })

#     @http.route('/dzh_sales_pipeline_retail_report_modify/dzh_sales_pipeline_retail_report_modify/objects/<model("dzh_sales_pipeline_retail_report_modify.dzh_sales_pipeline_retail_report_modify"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dzh_sales_pipeline_retail_report_modify.object', {
#             'object': obj
#         })