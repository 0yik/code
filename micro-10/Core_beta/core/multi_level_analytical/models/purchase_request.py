from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_purchases')
        res = super(PurchaseRequestLine, self).default_get(fields)
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


    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'request_line_id', string='Analytic Distribution')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account", string='Analytic Account Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('request_line_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(PurchaseRequestLine, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(PurchaseRequestLine, self).write(values)
        self.check_lines(self)
        return result


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_purchases')
        res = super(PurchaseRequisitionLine, self).default_get(fields)
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


    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'requisition_line_id', string='Analytic Distribution')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account", string='Analytic Account Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('requisition_line_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(PurchaseRequisitionLine, self).create(values)
        self.check_lines(line)
        return line


    @api.multi
    def write(self, values):
        result = super(PurchaseRequisitionLine, self).write(values)
        self.check_lines(self)
        return result

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id
        currency = partner.property_purchase_currency_id or requisition.company_id.currency_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = currency.id
        self.origin = requisition.name
        self.partner_ref = requisition.name  # to control vendor bill based on agreement reference
        self.notes = requisition.description
        self.date_order = requisition.date_end or fields.Datetime.now()
        self.picking_type_id = requisition.picking_type_id.id

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context({
                'lang': partner.lang,
                'partner_id': partner.id,
            })
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(
                    line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Compute price_unit in appropriate currency
            if requisition.company_id.currency_id != currency:
                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)
            print 'Analytic Distribution Lines  :   ', line.analytic_distribution_id
            analytical_distribution_line = []
            for ad_lines in line.analytic_distribution_id:
                analytical_distribution_line.append((0, 0, {
                    'rate': ad_lines.rate,
                    'analytic_level_id': ad_lines.analytic_level_id.id,
                    'analytic_account_id': ad_lines.analytic_account_id.id
                }))
            # Create PO line
            order_lines.append((0, 0, {
                'name': name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_po_id.id,
                'product_qty': product_qty,
                'price_unit': price_unit,
                'taxes_id': [(6, 0, taxes_ids)],
                'date_planned': requisition.schedule_date or fields.Date.today(),
                'procurement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                'account_analytic_id': line.account_analytic_id.id,
                'analytic_distribution_id': analytical_distribution_line,
            }))
            print 'Purchase Line :  ', order_lines
        self.order_line = order_lines