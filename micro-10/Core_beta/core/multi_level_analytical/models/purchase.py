from odoo import fields, models,api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        purchase = super(PurchaseOrder, self).create(vals)
        for po_line in purchase.order_line:
            for line_item in po_line.analytic_distribution_id:
                if line_item.rate:
                    line_rate = po_line.analytic_distribution_id.search([('purchase_line_id', '=', po_line.id), (
                    'analytic_level_id', '=', line_item.analytic_level_id.id)])
                    amount = [a.rate for a in line_rate]
                    if sum(amount) != 100:
                        raise ValidationError(
                            ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

        return purchase

    @api.multi
    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        for po_line in self.order_line:
            for line in po_line.analytic_distribution_id:
                if line.rate:
                    line_rate = po_line.analytic_distribution_id.search([('purchase_line_id', '=', po_line.id),('analytic_level_id', '=', line.analytic_level_id.id)])
                    amount = [a.rate for a in line_rate ]
                    if sum(amount) != 100:
                        raise ValidationError(
                            ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

        return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_purchases')
        res = super(PurchaseOrderLine, self).default_get(fields)
        if 'check_distribution' in fields:
            res['check_distribution'] = distribution_check
            res['check_analytic_account'] = self.user_has_groups('purchase.group_analytic_accounting')
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', '=', 'purchase.order')])
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
                'multi_level_analytical.analytic_distribution_for_purchases')
            line.check_analytic_account = self.user_has_groups('purchase.group_analytic_accounting')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'purchase_line_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

    # @api.model
    # def create(self, values):
    #     line = super(PurchaseOrderLine, self).create(values)
    #     if line:
    #         for line_item in line.analytic_distribution_id:
    #             if line_item.rate != 100:
    #                 line_rate = line.analytic_distribution_id.search([('purchase_line_id', '=', line.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
    #                 amount = [a.rate for a in line_rate ]
    #                 if sum(amount) != 100:
    #                     raise ValidationError(
    #                         ("Sum of the rate should be 100 for analytic account level and related anlytic account"))
    #     return line
    #
    # @api.multi
    # def write(self, values):
    #     result = super(PurchaseOrderLine, self).write(values)
    #     for line in self.analytic_distribution_id:
    #         if line.rate != 100:
    #             line_rate = self.analytic_distribution_id.search([('purchase_line_id', '=', self.id),('analytic_level_id', '=', line.analytic_level_id.id)])
    #             amount = [a.rate for a in line_rate ]
    #             if sum(amount) != 100:
    #                 raise ValidationError(
    #                     ("Sum of the rate should be 100 for analytic account level and related anlytic account"))
    #
    #     return result