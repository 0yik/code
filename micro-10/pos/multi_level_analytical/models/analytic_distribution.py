from odoo import fields, models,api


class account_analytic_distribution_line(models.Model):
    _name = 'account.analytic.distribution.line'

    @api.model
    def _get_analytic_account(self):
        analytic_account_ids = self.env['account.analytic.account'].search([('level_id', '=', self.analytic_level_id.id)])
        return [('id', 'in', analytic_account_ids and analytic_account_ids.ids or [])]


    rate = fields.Float(string='Rate (%)', digits=(32, 2), default=100.00, required=True)
    analytic_level_id = fields.Many2one('account.analytic.level', string='Analytic Category', required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', domain=_get_analytic_account, required=1)
    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', invisible=True)
    invoice_line_id = fields.Many2one('account.invoice.line', 'Account Invoice Line', invisible=True)
    sale_line_id = fields.Many2one('sale.order.line', 'Account Invoice Line', invisible=True)
    pos_line_id = fields.Many2one('pos.order.line', 'POS Order Line', invisible=True)
    pos_config_id = fields.Many2one('pos.config', 'POS Config', invisible=True)
    stock_move_id = fields.Many2one('stock.move', 'Stock Move', invisible=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary rule', invisible=True)
    hr_contract_id = fields.Many2one('hr.contract', 'Salary rule', invisible=True)
    expense_id = fields.Many2one('hr.expense', 'Expense', invisible=True)

    @api.onchange('analytic_level_id')
    def onchange_analytic_level_id(self):
        analytic_account_ids = []
        if self.analytic_level_id:
            analytic_account_prioritisation = self.env['analytic.account.prioritisation'].search(
                [('analytic_level_id', '=', self.analytic_level_id.id)])
            for aa in analytic_account_prioritisation:
                fields = aa.fields_id.name
                cr = self._cr
                if aa.model_list == 'res.users':
                    cr.execute("SELECT %s FROM res_users WHERE id = %s" % (fields, self.env.uid))
                elif aa.model_list == 'hr.employee':
                    cr.execute("SELECT %s FROM hr_employee WHERE id = %s" % (fields, self.env.user.employee_ids.id))
                elif aa.model_list == 'res.branches':
                    cr.execute("SELECT brnach_id FROM res_users WHERE id = %s" % (self.env.uid))
                elif aa.model_list == 'res.company':
                    cr.execute("SELECT company_id FROM res_users WHERE id = %s" % (self.env.uid))
                value_check = cr.fetchone()
                if value_check:
                    if aa.fields_id.ttype == 'many2one':
                        value_check = self.env[aa.fields_id.relation].browse(value_check).name
                    analytic_account_search = self.env['account.analytic.account'].search([('name', '=', value_check),('level_id', '=', self.analytic_level_id.id)], limit = 1).id
                    if analytic_account_search:
                        analytic_account_ids.append(analytic_account_search)
                    else:
                        analytic_account= self.env['account.analytic.account'].create({
                            'name': value_check,
                            'company_id': self.env.user.company_id.id,
                            'level_id': self.analytic_level_id.id,
                            'currency_id': self.env.user.company_id.currency_id.id,
                        })
                        analytic_account_ids.append(analytic_account.id)

        # result.update({'domain': {'analytic_account_id': [('id', 'in', analytic_account_ids and analytic_account_ids or False)]}})

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    analytic_level_id = fields.Many2one('account.analytic.level', string='Analytic Category', required=True)
    invoice_id = fields.Many2one('account.invoice', string='Source Reference')