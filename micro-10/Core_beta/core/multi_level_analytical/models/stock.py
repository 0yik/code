from odoo import fields, models,api
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def _check_distribution_account(self):
        for line in self:
            line.check_analytic_account = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_account_for_inventory')

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_inventory')
        res = super(StockMove, self).default_get(fields)
        if 'check_distribution' in fields:
            res['check_distribution'] = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_inventory')
            res['check_analytic_account'] = distribution_check
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', '=', 'stock.move')])
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
                'multi_level_analytical.analytic_distribution_for_inventory')
            line.check_analytic_account = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_account_for_inventory')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'stock_move_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, values):
        line = super(StockPicking, self).create(values)
        print
        for move_line in line.move_lines:
            for line_item in move_line.analytic_distribution_id:
                if line_item.rate:
                    line_rate = move_line.analytic_distribution_id.search(
                        [('stock_move_id', '=', move_line.id), ('analytic_level_id', '=', line_item.analytic_level_id.id)])
                    amount = [a.rate for a in line_rate]
                    if sum(amount) != 100:
                        raise ValidationError(
                            ("Sum of the rate should be 100 for analytic account level and related anlytic account"))
        return line

    @api.multi
    def write(self, values):
        result = super(StockPicking, self).write(values)
        for move_line in self.move_lines:
            for line in move_line.analytic_distribution_id:
                if line.rate:
                    line_rate = move_line.analytic_distribution_id.search(
                        [('stock_move_id', '=', move_line.id), ('analytic_level_id', '=', line.analytic_level_id.id)])
                    amount = [a.rate for a in line_rate]
                    if sum(amount) != 100:
                        raise ValidationError(
                            ("Sum of the rate should be 100 for analytic account level and related anlytic account"))
        return result
