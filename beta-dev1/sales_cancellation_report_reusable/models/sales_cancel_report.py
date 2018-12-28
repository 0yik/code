from odoo import models, fields, api

class sales_cancel_report(models.TransientModel):
    _name='sales.cancel.report'

    country = fields.Many2one('res.country','Country',domain=lambda self: [('code','in',['SG','MY','TH'])])
    sales_person = fields.Many2one('res.users','Sales Person')
    start_date = fields.Date(String="Start Date", required = True)
    end_date = fields.Date(String="End Date")
    invoice_refund_ids = fields.Many2many('account.invoice')
    country_ids = fields.Many2many('res.country')
    curency_rate_ids = fields.Many2many('res.currency.rate')
    product_ids = fields.Many2many('account.invoice.line')

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {
            'ids': self.ids,
            'model': 'sales.cancel.report',
            'from': self.read(['start_date', 'end_date', 'country', 'sales_person'])[0]
        }
        conditions = [('type','=','out_refund')]
        if data['from']['start_date']:
            conditions.append(('date_invoice', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('date_invoice', '<=', data['from']['end_date']))
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
            self.country_ids = self.env['res.country'].browse(data['from']['country'][0])
        self.invoice_refund_ids = self.env['account.invoice'].search(conditions,order='create_date asc')
        if not data['from']['country']:
            # country_ids = []
            # for invoice in self.invoice_refund_ids:
            #     if invoice.partner_id.country_id.id:
            #         esixt = False
            #         for item in country_ids:
            #             if item == invoice.partner_id.country_id.id:
            #                 esixt = True
            #         if not esixt:
            #             country_ids.append(invoice.partner_id.country_id.id)
            # self.country_ids = self.env['res.country'].browse(country_ids)
        # self.currency_ids = self.env['res.currency.rate'].search([])
            self.country_ids = self.env['res.country'].search([('code','in',['SG','MY','TH'])])
            currency_id = []
        for country in self.country_ids:
            currency_id.append(country.currency_id.id)
        self.curency_rate_ids = self.env['res.currency.rate'].search([('currency_id', 'in', currency_id)])
        for currency in currency_id:
            currency_obj = self.env['res.currency.rate'].search([('currency_id', '=', currency)])
            if len(currency_obj) > 1:
                raise UserError('Currency has different rate but same datetime.')

        self.product_ids = self.env['account.invoice.line'].search([])
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales_cancellation_report_reusable.sales_cancel_report',
        }

