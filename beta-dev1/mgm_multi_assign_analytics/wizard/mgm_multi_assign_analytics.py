from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def analytic_account(self):
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('mgm_multi_assign_analytics', 'mgm_multi_assign_analytics_form')[1]
        except ValueError:
            compose_form_id = False
        res = {
            'type': 'ir.actions.act_window',
            'name': 'Analytics Accounting',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mgm.multi.assign.analytics',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': {'default_name': self.id}
        }
        return res
   
   
class MgmMultiAssignAnalytics(models.TransientModel):
    _name = 'mgm.multi.assign.analytics'

    login_company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    multi_analytics_accounting_line = fields.One2many('multi.analytics.accounting', 'mgm_multi_assign_analytics_id', string='Analytic Accounting')

    @api.model
    def default_get(self, fields):
        res = super(MgmMultiAssignAnalytics, self).default_get(fields)
        account_analytic_level_records = self.env["account.analytic.level"].search([('name','in',['Location', 'Business Unit', 'Contract', 'Project', 'Asset', 'Department'])])
        line_vals = []

        for account_analytic_level_record in account_analytic_level_records:
            line_vals.append((0, 0, {'analytic_account_level_id': account_analytic_level_record.id,}))
        res.update({'multi_analytics_accounting_line':line_vals,})
        return res
    
    
    # @api.multi
    # def save_multi_analytics_accounting_line(self):
    #     account_analytic_line = self.env['account.analytic.line']
    #     active_id = self._context.get('active_id')
    #     current_record = self.env['sale.order'].browse(active_id)
    #     for record in self.multi_analytics_accounting_line:
    #         account_analytic_line.create({'name': record.analytic_account_level_id.name,
    #                                       'account_id': record.analytic_account_id.id or False,
    #                                       'amount': current_record.amount_total or False,})
    #     return True
    
    
class MultiAnalyticsAccounting(models.TransientModel):
    _name = 'multi.analytics.accounting'

    analytic_account_level_id = fields.Many2one('account.analytic.level', string='Analytic Account Level')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    mgm_multi_assign_analytics_id = fields.Many2one('mgm.multi.assign.analytics', string='Mgm Multi Assign Analytics')

