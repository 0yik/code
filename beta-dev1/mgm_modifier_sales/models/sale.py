from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    additional_price = fields.Float(string='Additional Price', store=True, compute='_compute_addtion_price',)
    additional_price_amount = fields.Float(string='Additional Price', store=True, related='additional_price')
    tmp_price = fields.Float()
    laycan_ids = fields.One2many('sale.laycan.lines', 'sale_id', 'Shipping Informations')
    mother_vessel= fields.Char('Mother Vessel')
    requisition_state = fields.Selection(related= 'requisition_id.business_unit.unit', store=True)
    asset= fields.Char('Asset')

    @api.depends('order_line.price_total','additional_price')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()
        for order in self:
            order.amount_total = order.amount_untaxed + order.amount_tax + order.additional_price_amount

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        if not self.requisition_id:
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.partner_id
        payment_term = partner.property_payment_term_id
        currency = requisition.company_id.currency_id

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
        self.mother_vessel = requisition.mother_vessel
        self.date_order = requisition.date_end or fields.Datetime.now()
        self.picking_type_id = requisition.picking_type_id.id
        self.pricelist_id = self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        self.partner_invoice_id = addr['invoice'],
        self.partner_shipping_id = addr['delivery'],
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
            if product_lang.description_sale:
                name += '\n' + product_lang.description_sale

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(
                    line.product_id.taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id))
            else:
                taxes_ids = line.product_id.taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_id:
                product_uom_qty = line.product_uom_id._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_id)
            else:
                product_uom_qty = line.product_uom_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_uom_qty = 0

            # Compute price_unit in appropriate currency
            if requisition.company_id.currency_id != currency:
                price_unit = requisition.company_id.currency_id.compute(price_unit, currency)

            # Create PO line
            order_lines.append((0, 0, {
                'name': name,
                'product_id': line.product_id.id,
                'product_uom': line.product_id.uom_id.id,
                'product_uom_qty': product_uom_qty,
                'price_unit': price_unit,
                'taxes_id': [(6, 0, taxes_ids)],
                'check_additional_price': True,
                'date_planned': requisition.schedule_date or fields.Date.today(),
                'procur ement_ids': [(6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                'account_analytic_id': line.account_analytic_id.id,
            }))

            #Map laycan into shipping information
            for laycan in requisition.laycan_ids:
                laycan.sale_id = self.id
        self.order_line = order_lines

    @api.onchange('additional_price')
    def onchange_additional_price(self):
        if self.additional_price:
            self.additional_price_amount = self.additional_price
            self.tmp_price = self.additional_price
            for line in self.order_line:
                if line.product_id.type == 'service' and line.check_additional_price:
                    line.check_additional_price = False

    @api.depends('order_line.product_id')
    def _compute_addtion_price(self):
        for order in self:
            if any ([line.check_additional_price for line in order.order_line]):
                additional_price = 0
                for line in order.order_line:
                    if line.product_id.type == 'service':
                        additional_price += line.product_id.additional_price
                order.additional_price = additional_price
                order.tmp_price = additional_price
            else:
                order.additional_price = order.tmp_price


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    check_additional_price = fields.Boolean(default=True)

    @api.depends('order_line.price_total', 'additional_price_amount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            print 'Additional price     =   ', self.additional_price
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax + order.additional_price,
            })


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.check_additional_price = True


class LaycanLines(models.Model):
    _inherit = 'sale.laycan.lines'

    sale_id = fields.Many2one('sale.order', 'Sale Reference')

LaycanLines()

class SaleReport(models.Model):
    _inherit = "sale.report"

    product_name = fields.Char(string="Product Name")
    product_code = fields.Char(string="Product Code")

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
                    sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                    sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
                    sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
                    sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
                    count(*) as nbr,
                    s.name as name,
                    s.date_order as date,
                    s.state as state,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.team_id as team_id,
                    p.product_tmpl_id,
                    t.name as product_name,
                    p.default_code as product_code,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
                    sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    t.name,
                    p.default_code,
                    s.name,
                    s.date_order,
                    s.partner_id,
                    s.user_id,
                    s.state,
                    s.company_id,
                    s.pricelist_id,
                    s.project_id,
                    s.team_id,
                    p.product_tmpl_id,
                    partner.country_id,
                    partner.commercial_partner_id
        """
        return group_by_str

SaleReport()
