from odoo import fields, models,api
from odoo.exceptions import ValidationError

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_pos')
        res = super(PosOrderLine, self).default_get(fields)
        if ('check_distribution' and 'check_analytic_account') in fields:
            res['check_analytic_account'] = self.user_has_groups('pos_analytic_by_config.group_analytic_accounting')
            res['check_distribution'] = distribution_check
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', '=', 'pos.order')])
            analytical_distribution_line = []
            for analytical_level in search_analytic_level:
                search_analytic_account = self.env['account.analytic.account'].search(
                    [('level_id', '=', analytical_level.id)], limit=1)
                analytical_distribution_line.append((0, 0, {
                    'rate': 100,
                    'analytic_level_id': analytical_level.id,
                    'analytic_account_id': search_analytic_account and search_analytic_account.id or ''
                }))
            res['analytic_distribution_id'] = analytical_distribution_line
        return res

    def _check_distribution_account(self):
        for line in self:
            line.check_distribution = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_pos')
            line.check_analytic_account = self.user_has_groups('pos_analytic_by_config.group_analytic_accounting')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'pos_line_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

    @api.multi
    def write(self, vals):
        if self.order_id and self.order_id.session_id and self.order_id.session_id.config_id and self.order_id.session_id.config_id.analytic_distribution_id:
            ad_line_vals = []
            for line in self.order_id.session_id.config_id.analytic_distribution_id:
                ad_line_vals.append((0,0, {'rate':line.rate, 'analytic_level_id':line.analytic_level_id.id, 'analytic_account_id':line.analytic_account_id.id}))
            vals.update({
                'analytic_distribution_id': ad_line_vals
            })
        return super(PosOrderLine, self).write(vals)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_pos')
        res = super(PosConfig, self).default_get(fields)
        if ('check_distribution' and 'check_analytic_account') in fields:
            res['check_analytic_account'] = self.user_has_groups('pos_analytic_by_config.group_analytic_accounting')
            res['check_distribution'] = distribution_check
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', '=', 'pos.order')])
            analytical_distribution_line = []
            for analytical_level in search_analytic_level:
                search_analytic_account = self.env['account.analytic.account'].search(
                    [('level_id', '=', analytical_level.id)], limit=1)
                analytical_distribution_line.append((0, 0, {
                    'rate': 100,
                    'analytic_level_id': analytical_level.id,
                    'analytic_account_id': search_analytic_account and search_analytic_account.id or ''
                }))
            res['analytic_distribution_id'] = analytical_distribution_line
        return res

    def _check_distribution_account(self):
        for line in self:
            line.check_distribution = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_pos')
            line.check_analytic_account = self.user_has_groups('pos_analytic_by_config.group_analytic_accounting')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'pos_config_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('pos_config_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(PosConfig, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(PosConfig, self).write(values)
        self.check_lines(self)
        return result

