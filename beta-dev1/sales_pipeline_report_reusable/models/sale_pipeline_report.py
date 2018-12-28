from odoo import models, fields, api

class crm_lead(models.TransientModel):
    _name    =  'sales.pipeline.report'

    start_date = fields.Date()
    end_date   = fields.Date()
    country_id = fields.Many2one(comodel_name='res.country')
    user_id    = fields.Many2one(comodel_name='res.users')
    lead_ids   = fields.Many2many('crm.lead')
    invoice_ids = fields.Many2many('account.invoice','account_invoice_sales_pipeline_report_rel','account_invoice_ids' ,'invoice_ids')

    @api.multi
    def print_report(self,context=None):
        self.ensure_one()

        data = {
            'ids'   : self.ids,
            'model' : 'sales.pipeline.report',
            'from'  : self.read(['start_date', 'end_date', 'country_id', 'user_id'])[0]
        }
        # condition for all table
        conditions = []
        if data['from']['start_date']:
            conditions.append(('create_date', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('create_date', '<=', data['from']['end_date']))
        if data['from']['country_id']:
            conditions.append(('country_id', '=', data['from']['country_id'][0]))
        if data['from']['user_id']:
            conditions.append(('user_id', '=', data['from']['user_id'][0]))
        self.lead_ids = self.env['crm.lead'].search(conditions)
        partner_ids = []
        for item in self.lead_ids:
            if item.partner_id.id and item.partner_id.ids:
                partner_ids.append(item.partner_id.id)
        self.invoice_ids = self.env['account.invoice'].search(['&',('partner_id','in',list(set(partner_ids))),('type','=','out_invoice')])

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales_pipeline_report_reusable.sales_pipeline_report',
        }
