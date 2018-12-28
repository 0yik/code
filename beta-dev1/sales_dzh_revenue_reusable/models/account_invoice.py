from odoo import models, fields, api
class res_partner(models.Model):
    _inherit = 'res.partner'
    # country_id required True
    country_id = fields.Many2one(comodel_name='res.country', required=True)

class account_invoice(models.TransientModel):
    _name = 'account.dzh.invoice'

    start_date  = fields.Date()
    end_date    = fields.Date()
    country_id  = fields.Many2one(comodel_name='res.country')
    user_id     = fields.Many2one(comodel_name='res.users')
    type_report = fields.Selection(
        [('out_invoice', 'Revenue'),
         ('out_refund', 'Refund')],
        string='Type Report', index=True,)
    invoice_refund_ids = fields.Many2many('account.invoice','sales_dzh_revenue_reusable_invoice_refund_ids_rel', 'account_dzh_invoice_ids', 'account_invoice_ids' )
    country_ids = fields.Many2many('res.country', 'sales_dzh_revenue_reusable_total_country_ids_rel', 'account_dzh_invoice_ids', 'country_ids' )

    @api.multi
    def print_report(self, context=None):
        self.ensure_one()

        data = {
            'ids': self.ids,
            'model': 'account.dzh.invoice',
            'from': self.read(['type_report','start_date', 'end_date', 'country_id', 'user_id'])[0]
        }

        conditions_for_all_table = []
        if data['from']['type_report']:
            if data['from']['type_report'] == 'out_invoice':
                conditions_for_all_table.append(('type', '=', data['from']['type_report']))
            elif data['from']['type_report'] == 'out_refund':
                conditions_for_all_table.append(('type', '=', data['from']['type_report']))

        if data['from']['start_date']:
            conditions_for_all_table.append(('create_date', '>=', data['from']['start_date']))

        if data['from']['end_date']:
            conditions_for_all_table.append(('create_date', '<=', data['from']['end_date']))

        if data['from']['user_id']:
            conditions_for_all_table.append(('user_id', '=' , data['from']['user_id'][0]))


        if data['from']['country_id']:
            partner_ids = self.env['res.partner'].search([('country_id', '=', data['from']['country_id'][0])])
            conditions_for_all_table.append(('partner_id', 'in', partner_ids))
            self.country_ids = self.env['res.country'].browse(data['from']['country_id'].id)


        self.invoice_refund_ids = self.env['account.invoice'].search(conditions_for_all_table, order='date_invoice asc')
        # get country_ids and not duplicate country
        if not data['from']['country_id']:
            if self.invoice_refund_ids and self.invoice_refund_ids.ids:
                country_id = []
                for id in self.invoice_refund_ids:
                    if id.partner_id.country_id.id:
                        esixt = False
                        for item in country_id:
                            if item == id.partner_id.country_id.id:
                                esixt = True
                        if not esixt:
                            country_id.append(id.partner_id.country_id.id)
                self.country_ids = self.env['res.country'].browse(country_id)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales_dzh_revenue_reusable.sales_revenue_report',
        }