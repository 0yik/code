
from odoo import fields, models,api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    group_analytic_distribution_for_purchases = fields.Boolean('Analytic distribution for purchases',
                                          implied_group='purchase.group_analytic_accounting',
                                      help="Allows you to specify an analytic distribution on purchase order lines.")

    @api.model
    def get_default_analytic_distribution_for_purchases(self, fields):
        group_analytic_distribution_for_purchases = False
        if 'group_analytic_distribution_for_purchases' in fields:
            group_analytic_distribution_for_purchases = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_purchases')
        return {
            'group_analytic_distribution_for_purchases': group_analytic_distribution_for_purchases
        }

    @api.multi
    def set_default_analytic_distribution_for_purchases(self):
        for model in self:
            self.env['ir.config_parameter'].sudo().set_param('multi_level_analytical.analytic_distribution_for_purchases',
                                                             model.group_analytic_distribution_for_purchases)
