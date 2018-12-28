# -*- coding: utf-8 -*-

import math
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class sales_pipeline_institutional_report(models.TransientModel):
    _name='sales.pipeline.institutional.report'

    country = fields.Many2one('res.country', 'Country')
    currency_ids = fields.Many2many('res.currency')
    curency_rate_ids = fields.Many2many('res.currency.rate')
    sales_person = fields.Many2one('res.users', 'Sales Person')
    start_date = fields.Date(String="Start Date", required=True)
    end_date = fields.Date(String="End Date")
    invoice_ids = fields.Many2many('crm.lead')
    currency_sin_obj = fields.Integer()
    invoice_filter = [{}]
    date_filter = ['']
    date_filter1 = ['']
    date_filter2 = ['']

    @api.multi
    def print_report(self):
        self.ensure_one()

        data = {
            'ids': self.ids,
            'model': 'sales.pipeline.institutional.report',
            'from': self.read(['start_date', 'end_date', 'country', 'sales_person'])[0]
        }

        conditions = [
            ('x_subscription_period', '>=', data['from']['start_date']),
            ('invoice_type', '=', 'fiancial'),
        ]
        if data['from']['end_date']:
            conditions.append(('x_subscription_period', '<=', data['from']['end_date']))
        if data['from']['sales_person']:
            conditions.append(('user_id', '=', data['from']['sales_person'][0]))
        if data['from']['country']:
            sales_team_ids = self.env['crm.team'].search([('country', '=', data['from']['country'][0])])
            sales_person = []
            for sales_team_id in sales_team_ids:
                for member_id in sales_team_id.member_ids:
                    sales_person.append(member_id.id)
            # partner_ids = self.env['res.partner'].search([('country_id', '=', data['from']['country'][0])])._ids
            conditions.append(('user_id', 'in', sales_person))

        # self.date_filter[0] = 'Potential Revenue as at {}'.format(datetime.strptime(data['from']['end_date'], "%Y-%m-%d").strftime("%d %b %Y"))
        self.invoice_ids = self.env['crm.lead'].search(conditions, order='user_id desc')
        # self.date_filter2[0] = 'New Sales Revenue as at {}'.format(datetime.strptime(data['from']['end_date'], "%Y-%m-%d").strftime("%d %b %Y"))
        self.currency_sin_obj = self.env['res.currency'].search([('name', '=', 'SGD')]).id

        currency_id = []
        self.date_filter1[0] = []
        count = 0
        for invoice_id in self.invoice_ids:
            crm_lead_obj = self.env['crm.lead'].search([('id', 'in', self.invoice_ids._ids),('user_id', '=', invoice_id.user_id.id)],
                                    order='probability desc')
            for crm_lead in crm_lead_obj:
                if crm_lead.id not in self.date_filter1[0]:
                    self.date_filter1[0].append(crm_lead.id)
            if invoice_id.currency_id:
                currency_id.append(invoice_id.currency_id.id)

        self.currency_ids = self.env['res.currency'].browse(currency_id)
        currency_id.append(self.currency_sin_obj)
        self.curency_rate_ids = self.env['res.currency.rate'].search([('currency_id','in',currency_id)])
        for currency in currency_id:
            currency_obj = self.env['res.currency.rate'].search([('currency_id', '=', currency)])
            if len(currency_obj) > 1:
                raise UserError('Currency has different rate but same datetime.')

        # self.currency = self.env['res.currency'].search([('name','=','SGD')])
        self.invoice_filter[0] = {}
        for invoice in self.invoice_ids:
            if invoice.team_id and invoice.team_id.country:
                if invoice.team_id.country.name in self.invoice_filter[0]:
                    self.invoice_filter[0][invoice.team_id.country.name]['ids'].append(invoice.id)
                else:
                    self.invoice_filter[0][invoice.team_id.country.name] = {
                        'ids': [invoice.id],
                    }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dzh__sales__pipeline__institutional-report__modify.sales__pipeline__institutional_report',
        }

