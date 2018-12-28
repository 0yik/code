# -*- coding: utf-8 -*-

import math
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import models, fields, api

class sales_cancel_report(models.TransientModel):
    _name='sales.revenue.report'

    country = fields.Many2one('res.country','Country')
    sales_person = fields.Many2one('res.users','Sales Person')
    start_date = fields.Date(String="Start Date", required = True)
    end_date = fields.Date(String="End Date", required = True)
    invoice_ids = fields.Many2many('account.invoice')
    invoice_filter = [{}]
    date_filter = [{}, {}]

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {
            'ids': self.ids,
            'model': 'sales.pipeline.report',
            'from': self.read(['start_date', 'end_date', 'country', 'sales_person'])[0]
        }

        conditions = [
            ('create_date', '>=', data['from']['start_date']),
            ('create_date', '<=', data['from']['end_date']),
        ]

        if data['from']['sales_person']:
            conditions.append(('user_id', '=', data['from']['sales_person'][0]))
        if data['from']['country']:
            partner_ids = self.env['res.partner'].search([('country_id','=',data['from']['country'][0])])._ids
            conditions.append(('partner_id','in',partner_ids))
        self.invoice_ids = self.env['account.invoice'].search(conditions,order='create_date asc')

        # Set date_filter
        start_date = datetime.strptime(data['from']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['from']['end_date'], '%Y-%m-%d')
        month_delta = int(math.floor((end_date.month - start_date.month)/2))
        middle_month = start_date + relativedelta(months=month_delta)

        self.date_filter[0] = {
            'name': '{}-{}'.format(start_date.strftime('%b'), middle_month.strftime('%b')),
            'datas': {},
        }
        self.date_filter[1] = {
            'name': '{}-{}'.format((middle_month + relativedelta(months=1)).strftime('%b'), end_date.strftime('%b')),
            'datas': {},
        }

        # Set invoice_filter
        self.invoice_filter[0] = {}
        for invoice in self.invoice_ids:
            sale_person = invoice.user_id and invoice.user_id.name or False
            country = invoice.partner_id and invoice.partner_id.country_id and invoice.partner_id.country_id.name or False
            name = country or sale_person
            if sale_person and country:
                name = '{} - {}'.format(sale_person, country)

            if name in self.invoice_filter[0]:
                self.invoice_filter[0][name].append(invoice.id)
            else:
                self.invoice_filter[0][name] = [invoice.id]

            if not name in self.date_filter[0]['datas']:
                self.date_filter[0]['datas'][name] = {
                    'ids': [],
                    'total_amount': 0,
                    'total_annualised': 0,
                }
            if not name in self.date_filter[1]['datas']:
                self.date_filter[1]['datas'][name] = {
                    'ids': [],
                    'total_amount': 0,
                    'total_annualised': 0,
                }
            start_date_month = datetime.strptime(invoice.x_subscription_period, '%Y-%m-%d').month
            if start_date_month <= middle_month.month:
                if name in self.date_filter[0]['datas']:
                    self.date_filter[0]['datas'][name]['ids'].append(invoice.id)
                    self.date_filter[0]['datas'][name]['total_amount'] += invoice.amount_total
                    self.date_filter[0]['datas'][name]['total_annualised'] += invoice.amount_total*invoice.x_month_number
            else:
                self.date_filter[1]['datas'][name]['ids'].append(invoice.id)
                self.date_filter[1]['datas'][name]['total_amount'] += invoice.amount_total
                self.date_filter[1]['datas'][name]['total_annualised'] += invoice.amount_total * invoice.x_month_number

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales_revenue_report_reusable.sales_revenue_report',
        }

