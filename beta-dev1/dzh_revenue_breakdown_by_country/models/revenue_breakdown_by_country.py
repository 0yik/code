# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class dzh_revenue_breakdown_by_country(models.TransientModel):
    _name = 'revenue.breakdown.by.country'

    country = fields.Many2one('res.country','Country')
    sales_person = fields.Many2one('res.users', 'Sales Person')
    start_date = fields.Date(String="Start Date", required = True)
    end_date = fields.Date(String="End Date")
    # user_ids = fields.Many2many('dzh.partner.user')
    currency_ids = fields.Many2many('res.currency')
    curency_rate_ids = fields.Many2many('res.currency.rate')
    customer_ids = fields.Many2many('res.partner')
    account_invoice = fields.Many2many('account.invoice')
    country_ids = fields.Many2many('res.country')
    member_type_ids = fields.Many2many('member.type')
    not_country_filter = fields.Integer(default = 0)

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {
            'ids': self.ids,
            'model': 'revenue.breakdown.by.country',
            'from': self.read(['start_date', 'end_date','sales_person', 'country'])[0]
        }
        conditions = []
        if data['from']['start_date']:
            conditions.append(('create_date', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('create_date', '<=', data['from']['end_date']))
        if data['from']['sales_person']:
            conditions.append(('user_id','=',data['from']['sales_person'][0]))
        if data['from']['country']:
            sales_team_ids = self.env['crm.team'].search([('country', '=', data['from']['country'][0])])
            sales_person = []
            for sales_team_id in sales_team_ids:
                for member_id in sales_team_id.member_ids:
                    sales_person.append(member_id.id)
            conditions.append(('user_id', 'in', sales_person))
            self.not_country_filter = 0
            self.country_ids = self.env['res.country'].browse(data['from']['country'][0])
        self.account_invoice = self.env['account.invoice'].search(conditions)
        if not data['from']['country']:
            self.not_country_filter = 1
            country_ids = []
            for invoice in self.account_invoice:
                if invoice.team_id and invoice.team_id.country.id:
                    esixt = False
                    for item in country_ids:
                        if item == invoice.team_id.country.id:
                            esixt = True
                    if not esixt:
                        country_ids.append(invoice.team_id.country.id)
            self.country_ids = self.env['res.country'].browse(country_ids)

        currency_id = []
        for country in self.country_ids:
            currency_id.append(country.currency_id.id)

        self.currency_ids = self.env['res.currency'].browse(currency_id)
        self.curency_rate_ids = self.env['res.currency.rate'].search([('currency_id', 'in', currency_id)])
        for currency in currency_id:
            currency_obj = self.env['res.currency.rate'].search([('currency_id', '=', currency)])
            if len(currency_obj) > 1:
                raise UserError('Currency has different rate but same datetime.')

        if self.account_invoice:
            customer_ids = []
            for invoice in self.account_invoice:
                if invoice.partner_id:
                    esixt = False
                    for item in customer_ids:
                        if item == invoice.partner_id.id:
                            esixt = True
                    if not esixt:
                        customer_ids.append(invoice.partner_id.id)
            self.customer_ids = self.env['res.partner'].browse(customer_ids)
        self.member_type_ids = self.env['member.type'].search([])

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dzh_revenue_breakdown_by_country.revenue_breakdown_by_country_report',
        }

