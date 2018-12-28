# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from datetime import datetime, date, timedelta
import math
from dateutil.relativedelta import relativedelta
from functools import partial
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api, _


class report_crm_report_document(osv.AbstractModel):
    _name = 'report.avanta_crm_report.report_crm_report_document'
    _inherit = 'report.abstract_report'

    # _template = 'avanta_crm_report.report_crm_report_document'
    # _wrapped_report_class = crm_report_parser

    @api.model
    def get_data(self, data):
        print '================------------==============='
        user_id = data['user_id'] and data['user_id'][0]
        services = data['services'] and data['services'][0]
        products = data['products'] and data['products'][0]
        company_id = data['company_id'] and data['company_id'][0]
        date_start = data['date_start']
        date_end = data['date_end']
        all = data['all']
        all_details = data['all_details']

        crm_ids = []
        result = []
        if all == True:
            query = """SELECT partner_id FROM crm_lead
                                WHERE active = True
                                AND date_last_stage_update >= '%s' AND date_last_stage_update <= '%s' and company_id = %s """ % (
            date_start + ' 00:00:00', date_end + ' 23:59:59', company_id)
        elif all_details == True:
            print 'TEST ALL SERVICE AND PRODUCTS==================================\n' * 10
            query = """SELECT partner_id FROM crm_lead
                                WHERE active = True
                                AND date_last_stage_update >= '%s' AND date_last_stage_update <= '%s' and company_id = %s and user_id = %s""" % (
            date_start + ' 00:00:00', date_end + ' 23:59:59', company_id, user_id)
        else:
            query = """SELECT partner_id FROM crm_lead
                                            WHERE user_id = %s AND services = %s AND products = %s AND active = True
                                            AND date_last_stage_update >= '%s' AND date_last_stage_update <= '%s' and company_id = %s """ % (
            user_id, services, products, date_start + ' 00:00:00', date_end + ' 23:59:59', company_id)
        self.env.cr.execute(query)

        customer_ids = list(set(map(lambda x: x[0], self.env.cr.fetchall())))
        # internal Reference
        int_ref_list = []
        # Grand Services
        total_items_0 = 0
        total_amount_0 = 0.0
        # Grand Products
        total_items_1 = 0
        total_amount_1 = 0.0
        # Grand Enquiry
        total_items_2 = 0
        total_amount_2 = 0.0
        # Grand Allocation
        total_items_3 = 0
        total_amount_3 = 0.0
        # Grand Follow up
        total_items_4 = 0
        total_amount_4 = 0.0
        # Grand Quotation
        total_items_5 = 0
        total_amount_5 = 0.0
        # Grand Won
        total_items_6 = 0
        total_amount_6 = 0.0
        # Grand Lost
        total_items_7 = 0
        total_amount_7 = 0.0

        for customer in customer_ids:
            vals = {
                'customer_name': '',
                # internal Reference
                'internal_reference': '',
                # Services
                'items_0': 0,
                'amount_0': 0.0,
                # Products
                'items_1': 0,
                'amount_1': 0.0,
                # Enquiry
                'items_2': 0,
                'amount_2': 0.0,
                # Allocation
                'items_3': 0,
                'amount_3': 0.0,
                # Follow up
                'items_4': 0,
                'amount_4': 0.0,
                # Quotation
                'items_5': 0,
                'amount_5': 0.0,
                # Won
                'items_6': 0,
                'amount_6': 0.0,
                # Lost
                'items_7': 0,
                'amount_7': 0.0,
            }

            if all == True:
                crm_ids = self.env['crm.lead'].search([('active', '=', True), ('company_id', '=', company_id),
                                                       ('date_last_stage_update', '>=', date_start + ' 00:00:00'),
                                                       ('date_last_stage_update', '<=', date_end + ' 23:59:59')])
            elif all_details == True:
                crm_ids = self.env['crm.lead'].search([('active', '=', True), ('company_id', '=', company_id),
                                                       ('user_id', '=', user_id), ('partner_id', '=', customer),
                                                       ('date_last_stage_update', '>=', date_start + ' 00:00:00'),
                                                       ('date_last_stage_update', '<=', date_end + ' 23:59:59')])
            else:
                crm_ids = self.env['crm.lead'].search([('user_id', '=', user_id),
                                                       ('services', '=', services),
                                                       ('products', '=', products),
                                                       ('partner_id', '=', customer),
                                                       ('active', '=', True),
                                                       ('company_id', '=', company_id),
                                                       ('date_last_stage_update', '>=', date_start + ' 00:00:00'),
                                                       ('date_last_stage_update', '<=', date_end + ' 23:59:59')])
            total_items = len(crm_ids)
            partner = self.env['res.partner'].browse([customer])
            vals['customer_name'] = partner.name

            for l in crm_ids:
                if l.stage_id.name == 'Enquiry':
                    vals['items_0'] = total_items
                    vals['items_1'] = total_items
                    # Grand Services
                    total_items_0 += total_items
                    total_items_1 += total_items
                    vals['amount_0'] += l.planned_revenue
                    vals['amount_1'] += l.planned_revenue
                    # Grand Products and Services
                    total_amount_0 += l.planned_revenue
                    total_amount_1 += l.planned_revenue
                    # Enquiry
                    vals['items_2'] += 1
                    vals['amount_2'] += l.planned_revenue
                    # Grand Enquiry
                    total_items_2 += 1
                    total_amount_2 += l.planned_revenue
                elif l.stage_id.name == 'Allocation':
                    vals['items_0'] = total_items
                    vals['items_1'] = total_items
                    # Grand Services
                    total_items_0 += total_items
                    total_items_1 += total_items
                    vals['amount_0'] += l.products.list_price
                    vals['amount_1'] += l.products.list_price
                    # Grand Products
                    total_amount_0 += l.products.list_price
                    total_amount_1 += l.products.list_price
                    # Allocation
                    vals['items_3'] += 1
                    vals['amount_3'] += l.products.list_price
                    # Grand Allocation
                    total_items_3 += 1
                    total_amount_3 += l.products.list_price
                elif l.stage_id.name == 'Follow up':
                    if l.quotation_preferred == True and l.sale_number > 0:
                        for order in l.order_ids:
                            for lines in order.order_line:
                                # internal Reference
                                int_ref_list.append(lines.product_id.default_code)
                                vals['items_0'] = total_items
                                vals['items_1'] = total_items
                                # Grand Services
                                total_items_0 += total_items
                                total_items_1 += total_items
                                vals['amount_0'] += order.services_id.list_price
                                vals['amount_1'] += lines.price_unit
                                # Grand Products
                                total_amount_0 += order.services_id.list_price
                                total_amount_1 += lines.price_unit
                                # Follow up
                                vals['items_4'] += 1
                                vals['amount_4'] += order.amount_total
                                # Grand Follow up
                                total_items_4 += 1
                                total_amount_4 += order.amount_total
                    else:
                        vals['items_0'] = total_items
                        vals['items_1'] = total_items
                        # Grand Services
                        total_items_0 += total_items
                        total_items_1 += total_items
                        vals['amount_0'] += l.services.list_price
                        vals['amount_1'] += l.products.list_price
                        # Grand Products
                        total_amount_0 += l.services.list_price
                        total_amount_1 += l.products.list_price
                        # Follow up
                        vals['items_4'] += 1
                        vals['amount_4'] += l.products.list_price
                        # Grand Follow up
                        total_items_4 += 1
                        total_amount_4 += l.products.list_price
                elif l.stage_id.name == 'Quotation':
                    if l.quotation_preferred == True and l.sale_number > 0:
                        for order in l.order_ids:
                            for lines in order.order_line:
                                # internal Reference
                                int_ref_list.append(lines.product_id.default_code)
                                vals['items_0'] = total_items
                                vals['items_1'] = total_items
                                # Grand Services
                                total_items_0 += total_items
                                total_items_1 += total_items
                                vals['amount_0'] += order.services_id.list_price
                                vals['amount_1'] += lines.price_unit
                                # Grand Products
                                total_amount_0 += order.services_id.list_price
                                total_amount_1 += lines.price_unit
                                # Quotation
                                vals['items_5'] += 1
                                vals['amount_5'] += order.amount_total
                                # Grand Quotation
                                total_items_5 += 1
                                total_amount_5 += order.amount_total
                    else:
                        vals['items_0'] = total_items
                        vals['items_1'] = total_items
                        # Grand Services
                        total_items_0 += total_items
                        total_items_1 += total_items
                        vals['amount_0'] += l.services.list_price
                        vals['amount_1'] += l.products.list_price
                        # Grand Products
                        total_amount_0 += l.services.list_price
                        total_amount_1 += l.products.list_price
                        # Quotation
                        vals['items_5'] += 1
                        vals['amount_5'] += l.products.list_price
                        # Grand Quotation
                        total_items_5 += 1
                        total_amount_5 += l.products.list_price
                    continue
                elif l.stage_id.name == 'Status' and l.crm_lead_status == 'won':
                    if l.quotation_preferred == True and l.sale_number > 0:
                        for order in l.order_ids:
                            for lines in order.order_line:
                                # internal Reference
                                int_ref_list.append(lines.product_id.default_code)
                                vals['items_0'] = total_items
                                vals['items_1'] = total_items
                                # Grand Services
                                total_items_0 += total_items
                                total_items_1 += total_items
                                vals['amount_0'] += order.services_id.list_price
                                vals['amount_1'] += lines.price_unit
                                # Grand Products
                                total_amount_0 += order.services_id.list_price
                                total_amount_1 += lines.price_unit
                                # Won
                                vals['items_6'] += 1
                                vals['amount_6'] += order.amount_total
                                # Grand Won
                            total_items_6 += 1
                            total_amount_6 += order.amount_total
                    else:
                        vals['items_0'] = total_items
                        vals['items_1'] = total_items
                        # Grand Services
                        total_items_0 += total_items
                        total_items_1 += total_items
                        vals['amount_0'] += l.services.list_price
                        vals['amount_1'] += l.products.list_price
                        # Grand Products
                        total_amount_0 += l.services.list_price
                        total_amount_1 += l.products.list_price
                        vals['items_6'] += 1
                        vals['amount_6'] += l.products.list_price
                        total_items_6 += 1
                        total_amount_6 += l.products.list_price
                    continue

                elif l.stage_id.name == 'Status' and l.crm_lead_status == 'lost':
                    if l.quotation_preferred == True and l.sale_number > 0:
                        for order in l.order_ids:
                            for lines in order.order_line:
                                # internal Reference
                                int_ref_list.append(lines.product_id.default_code)
                                vals['items_0'] = total_items
                                vals['items_1'] = total_items
                                # Grand Services
                                total_items_0 += total_items
                                total_items_1 += total_items
                                vals['amount_0'] += order.services_id.list_price
                                vals['amount_1'] += lines.price_unit
                                # Grand Products
                                total_amount_0 += order.services_id.list_price
                                total_amount_1 += lines.price_unit
                                # Lost
                                vals['items_7'] += 1
                                vals['amount_7'] += order.amount_total
                                # Grand Lost
                                total_items_7 += 1
                                total_amount_7 += order.amount_total
                    else:
                        vals['items_0'] = total_items
                        vals['items_1'] = total_items
                        # Grand Services
                        total_items_0 += total_items
                        total_items_1 += total_items
                        vals['amount_0'] += l.services.list_price
                        vals['amount_1'] += l.products.list_price
                        # Grand Products
                        total_amount_0 += l.services.list_price
                        total_amount_1 += l.products.list_price
                        # Lost
                        vals['items_7'] += 1
                        vals['amount_7'] += l.products.list_price
                        # Grand Lost
                        total_items_7 += 1
                        total_amount_7 += l.products.list_price
            int_ref_text = ''
            for internal_text in set(int_ref_list):
                if internal_text:
                    int_ref_text += internal_text + " ,"
            vals['internal_reference'] = int_ref_text
            result.append(vals)
        return result

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_data': self.get_data,
        }
        return self.env['report'].render('avanta_crm_report.report_crm_report_document', docargs)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


