from odoo import fields, models,api


class ResBranch(models.Model):
    _inherit = 'res.branch'

    @api.model
    def create(self, vals):
        IrConfigParam = self.env['ir.config_parameter']
        result = super(ResBranch, self).create(vals)
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_branches')
        analytic_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_account_for_branches')
        if analytic_check:
            AnalyticAccount = self.env['account.analytic.account']
            AnalyticAccountLevel = self.env['account.analytic.level']
            analytic_account_search = AnalyticAccount.search([('name', '=', result.name)])
            if not analytic_account_search:
                analytic_level = AnalyticAccountLevel.search([('name', '=', 'Branches')], limit=1)
                if not analytic_level:
                    analytic_level = AnalyticAccountLevel.create({
                        'name': result.name})
                analytic_account = self.env['account.analytic.account'].create({
                    'name': result.name,
                    'company_id': self.env.user.company_id.id,
                    'level_id': analytic_level.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                })
        return result

class ResCompanies(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        IrConfigParam = self.env['ir.config_parameter']
        result = super(ResCompanies, self).create(vals)
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_companies')
        analytic_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_account_for_companies')
        if analytic_check:
            AnalyticAccount = self.env['account.analytic.account']
            AnalyticAccountLevel = self.env['account.analytic.level']
            analytic_account_search = AnalyticAccount.search([('name', '=', result.name)])
            if not analytic_account_search:
                analytic_level = AnalyticAccountLevel.search([('name', '=', 'Companies')], limit=1)
                if not analytic_level:
                    analytic_level = AnalyticAccountLevel.create({
                        'name': result.name})
                analytic_account = self.env['account.analytic.account'].create({
                    'name': result.name,
                    'company_id': self.env.user.company_id.id,
                    'level_id': analytic_level.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                })
        return result

