from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

from lxml import etree
from odoo.osv.orm import setup_modifiers

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(SaleOrder, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
    #     doc = etree.XML(result['arch'])
    #     distribution_check = self.env['ir.config_parameter'].sudo().get_param(
    #         'multi_level_analytical.analytic_distribution_for_sale')
    #     print 'Fields       :   ', result['fields'], '\n\n\nDistribution Check  :   ', distribution_check
    #     if distribution_check:
    #         for node in doc.xpath("//field[@name='order_line']//tree//field[@name='account_analytic_id']"):
    #             print 'Node :   ', node
    #             node.set('invisible', '1')
    #             setup_modifiers(node, result['fields']['account_analytic_id'])
    #             print 'String   :   ', etree.tostring(doc)
    #             result['arch'] = etree.tostring(doc)
    #     asd
    #     return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']

        res = super(SaleOrderLine, self).default_get(fields)
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_sale')
        if ('check_distribution' and 'check_analytic_account') in fields:
            res['check_distribution'] = distribution_check
            res['check_analytic_account'] = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_account_for_sales')
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', '=', 'sale.order')])
            analytical_distribution_line = []
            for analytical_level in search_analytic_level:
                search_analytic_account = self.env['account.analytic.account'].search([('level_id', '=', analytical_level.id)], limit = 1 )
                analytical_distribution_line.append((0, 0, {
                    'rate': 100,
                    'analytic_level_id' : analytical_level.id,
                    'analytic_account_id' : search_analytic_account and search_analytic_account.id or ''
                }))
            res['analytic_distribution_id'] = analytical_distribution_line
        return res

    def _check_distribution_account(self):
        IrConfigParam = self.env['ir.config_parameter']
        for line in self:
            line.check_distribution = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_sale')
            line.check_analytic_account = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_account_for_sales')


    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'sale_line_id', string='Analytic Distribution')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account", string='Analytic Account Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('sale_line_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(SaleOrderLine, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(SaleOrderLine, self).write(values)
        self.check_lines(self)
        return result

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        dist_lines = []
        for line in  self.analytic_distribution_id:
            dist_lines.append((0, 0,{
                'rate' :  line.rate,
                'analytic_level_id' : line.analytic_level_id.id,
                'analytic_account_id' : line.analytic_account_id.id
                 }))
        res.update({'analytic_distribution_id': dist_lines})
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if res and res.id:
            for line in res.invoice_line_ids:
                for sale_line in line.sale_line_ids:
                    if sale_line.analytic_distribution_id:
                        line.analytic_distribution_id = sale_line.analytic_distribution_id
        return res


