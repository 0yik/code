import math
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class pipeline_trading(models.TransientModel):
    _name = 'pipeline.trading.report'

    start_date = fields.Date()
    end_date = fields.Date()
    country_id = fields.Many2one(comodel_name='res.country')
    user_id = fields.Many2one(comodel_name='res.users')
    pipeline_ids = fields.Many2many('crm.lead')
    country_ids = fields.Many2many('res.country')
    date_filter = ['']
    date_filter1 = ['']
    date_filter2 = ['']
    currency_ids = fields.Many2many('res.currency')
    curency_rate_ids = fields.Many2many('res.currency.rate')
    currency_sin_obj = fields.Integer()

    @api.multi
    def print_trading_report(self, context=None):
        self.ensure_one()

        data = {
            'ids': self.ids,
            'model': 'pipeline.trading.report',
            'from': self.read(['start_date', 'end_date', 'country_id', 'user_id'])[0]
        }
        # condition for all table
        conditions = []
        conditions.append(('invoice_type', 'in', ('trading_gts','trading_dzh')))
        conditions.append(('market_segment_id', '=', 'Corporate Retail'))

        if data['from']['start_date']:
            conditions.append(('x_subscription_period', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('x_subscription_period', '<=', data['from']['end_date']))
        if data['from']['country_id']:
            sales_team_ids = self.env['crm.team'].search([('country', '=', data['from']['country_id'][0])])
            sales_person = []
            for sales_team_id in sales_team_ids:
                for member_id in sales_team_id.member_ids:
                    sales_person.append(member_id.id)
            # partner_ids = self.env['res.partner'].search([('country_id', '=', data['from']['country'][0])])._ids
            conditions.append(('user_id', 'in', sales_person))
            self.country_ids = self.env['res.country'].browse(data['from']['country_id'][0])
        if data['from']['user_id']:
            conditions.append(('user_id', '=', data['from']['user_id'][0]))

        # self.date_filter[0] = 'Potential Revenue as at {}'.format(datetime.strptime(data['from']['end_date'], "%Y-%m-%d").strftime("%d %b %Y"))
        # self.date_filter2[0] = 'New Sales Revenue as at {}'.format(datetime.strptime(data['from']['end_date'], "%Y-%m-%d").strftime("%d %b %Y"))
        self.pipeline_ids = self.env['crm.lead'].search(conditions, order='user_id desc')
        self.currency_sin_obj = self.env['res.currency'].search([('name', '=', 'SGD')]).id

        currency_id = []
        self.date_filter1[0] = []
        count = 0
        for pipeline_id in self.pipeline_ids:
            crm_lead_obj = self.env['crm.lead'].search(
                [('id', 'in', self.pipeline_ids._ids), ('user_id', '=', pipeline_id.user_id.id)],
                order='probability desc')
            for crm_lead in crm_lead_obj:
                if crm_lead.id not in self.date_filter1[0]:
                    self.date_filter1[0].append(crm_lead.id)
            if pipeline_id.currency_id:
                currency_id.append(pipeline_id.currency_id.id)

        self.currency_ids = self.env['res.currency'].browse(currency_id)
        currency_id.append(self.currency_sin_obj)
        self.curency_rate_ids = self.env['res.currency.rate'].search([('currency_id', 'in', currency_id)])
        for currency in currency_id:
            currency_obj = self.env['res.currency.rate'].search([('currency_id', '=', currency)])
            if len(currency_obj) > 1:
                raise UserError('Currency has different rate but same datetime.')

        self.currency_ids = self.env['res.currency'].browse(currency_id)

        if not data['from']['country_id']:
            country_id = []
            country_id.append(self.env['res.country'].search([('code','=','SG')]).id)
            if self.pipeline_ids and self.pipeline_ids.ids:
                for id in self.pipeline_ids:
                    if id.team_id and id.team_id.country.id:
                        esixt = False
                        for item in country_id:
                            if item == id.team_id.country.id:
                                esixt = True
                        if not esixt:
                            country_id.append(id.team_id.country.id)
            self.country_ids = self.env['res.country'].browse(country_id)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dzh_sales_pipeline_trading_report_modify.pipeline_trading_report',
        }
