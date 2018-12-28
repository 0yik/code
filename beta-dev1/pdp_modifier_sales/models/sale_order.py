from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total', 'additional_price', 'discount_type', 'discount_rate', 'cal_add_price')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        unit_price = 0
        total_netto = 0
        discount_rate_value = 0

        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0

            for line in order.order_line:
                unit_price = unit_price + (line.product_id.lst_price * line.product_uom_qty)
                total_netto = total_netto + (line.price_unit * line.product_uom_qty) - line.price_subtotal
                amount_untaxed += (line.product_uom_qty * line.price_unit)
                amount_tax += line.price_tax
                if line.custom_discount_type == 'percent':
                    amount_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100
                            order.amount_discount = (calculate_discount + order.discount_rate)
                            discount_rate_value = order.amount_discount

                else:
                    amount_discount += (line.custom_discount_rate)
                    if order.discount_type == 'percent':
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100
                            order.amount_discount = calculate_discount + ((amount_untaxed * order.discount_rate) / 100)
                            discount_rate_value = order.amount_discount

                    else:
                        calculate_discount = 0
                        if order.discount_rate:
                            for line in order.order_line:
                                calculate_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100
                            order.amount_discount = (calculate_discount + order.discount_rate)
                            discount_rate_value = order.amount_discount

            untaxed_amount = order.pricelist_id.currency_id.round(amount_untaxed)

            if order.discount_type and order.discount_rate:
                order.update({
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                    'amount_discount': order.pricelist_id.currency_id.round(discount_rate_value),
                    'amount_total': untaxed_amount - discount_rate_value + amount_tax + order.additional_price,
                    'cal_add_price': order.additional_price,
                    'total_bruto': unit_price,
                    'total_netto': (untaxed_amount - discount_rate_value) + order.additional_price,
                })

            else:
                order.update({
                    'amount_untaxed': untaxed_amount,
                    'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                    'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                    'amount_total': untaxed_amount - amount_discount + amount_tax + order.additional_price,
                    'cal_add_price': order.additional_price,
                    'total_bruto': unit_price,
                    'total_netto': (untaxed_amount - amount_discount) + order.additional_price,
                })

    additional_price = fields.Float('Additional Fee')
    total_bruto = fields.Float('Total Bruto', store=True, readonly=True, compute='_amount_all')
    total_netto = fields.Float('Total Netto', store=True, readonly=True, compute='_amount_all')
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits_compute=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits_compute=dp.get_precision('Account'), track_visibility='always')
    cal_add_price = fields.Float(string='Additional Fee', store=True, readonly=True, compute='_amount_all')

    @api.onchange('discount_type', 'discount_rate', 'additional_price')
    def supply_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                calculate_discount = 0
                if order.discount_rate:
                    for line in order.order_line:
                        calculate_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100
                    order.amount_discount = calculate_discount + ((order.amount_untaxed * order.discount_rate) / 100)
                    order.amount_total = order.amount_untaxed - order.amount_discount + order.amount_tax + order.additional_price

            else:
                calculate_discount = 0
                if order.discount_rate:
                    for line in order.order_line:
                        calculate_discount += (line.product_uom_qty * line.price_unit * line.custom_discount_rate) / 100

                    order.amount_discount = (calculate_discount + order.discount_rate)
                    order.amount_total = order.amount_untaxed - order.amount_discount + order.amount_tax + order.additional_price


class stock_move(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_from_move(self):
        origin = (self.group_id and (self.group_id.name + ":") or "") + (
                    self.rule_id and self.rule_id.name or self.origin or self.picking_id.name or "/")
        group_id = self.group_id and self.group_id.id or False
        if self.rule_id:
            if self.rule_id.group_propagation_option == 'fixed' and self.rule_id.group_id:
                group_id = self.rule_id.group_id.id
            elif self.rule_id.group_propagation_option == 'none':
                group_id = False
        return {
            'name': self.rule_id and self.rule_id.name or "/",
            'origin': origin,
            'company_id': self.company_id.id,
            'date_planned': self.date,
            'product_id': self.product_id.id,
            'product_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'location_id': self.location_id.id,
            'move_dest_id': self.id,
            'group_id': group_id,
            'route_ids': [(4, x.id) for x in self.route_ids],
            'warehouse_id': self.warehouse_id.id or (
                        self.picking_type_id and self.picking_type_id.warehouse_id.id or False),
            'priority': self.priority,
            'branch_id': self.branch_id.id
        }


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)
    custom_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Fixed Amount')], 'Discount Type', )
    custom_discount_rate = fields.Float(string='Discount Rate', required=1)

    @api.depends('product_uom_qty', 'discount', 'custom_discount_rate', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.custom_discount_type == 'percent':
                discount_amount = ((line.price_unit * line.product_uom_qty) * line.custom_discount_rate) / 100
                price = (line.price_unit * line.product_uom_qty) - discount_amount
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                  product=line.product_id, partner=line.order_id.partner_id)

                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

            else:
                price = (line.price_unit * line.product_uom_qty) - line.custom_discount_rate
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                  product=line.product_id, partner=line.order_id.partner_id)

                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })



    @api.onchange('custom_discount_type', 'custom_discount_rate')
    def discount_onchange(self):
        for rec in self:
            if rec.custom_discount_type and rec.custom_discount_rate:
                subtotal = rec.price_unit * rec.product_uom_qty
                price = 0
                total_included = 0.0
                if rec.custom_discount_type == 'percent':
                    discount_amount = ((rec.price_unit * rec.product_uom_qty) * rec.custom_discount_rate) / 100
                    price = (rec.price_unit * rec.product_uom_qty) - discount_amount
                    taxes = rec.tax_id.compute_all(price, rec.order_id.currency_id, 1,
                                                     product=rec.product_id, partner=rec.order_id.partner_id)
                    rec.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })

                else:
                    price = rec.price_unit
                    taxes = rec.tax_id.compute_all(price, rec.order_id.currency_id, rec.product_uom_qty,
                                                    product=rec.product_id, partner=rec.order_id.partner_shipping_id)
                    total_included = taxes['total_included'] - rec.custom_discount_rate
                rec.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })


    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        for line in res:
            if line.order_id:
                order_lines = self.env['sale.order.line'].search([('order_id.id', '=', line.order_id.id),
                                                                      ('product_id.id', '=', line.product_id.id),
                                                                      ('price_unit', '=', line.price_unit),
                                                                      ('product_uom.id', '=', line.product_uom.id),
                                                                      ('custom_discount_type', '=', line.custom_discount_type),
                                                                      ('custom_discount_rate', '=', line.custom_discount_rate),
                                                                  ])

                if len(order_lines) > 1:
                    self._cr.execute('''select product_uom_qty from sale_order_line where id=%s''' % (order_lines[0].id))
                    order_lines_qty = [x[0] for x in self.env.cr.fetchall()]
                    total_qty = order_lines[1].product_qty + order_lines_qty[0]

                    self._cr.execute('''update sale_order_line set product_uom_qty = %s where id=%s''' % (total_qty, order_lines[0].id))
                    self._cr.commit()
                    self._cr.execute('''delete from sale_order_line where id=%s''' % (order_lines[1].id))
                    self._cr.commit()


    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)

        for line in self:
            if line.order_id:
                order_lines = self.env['sale.order.line'].search([('order_id.id', '=', line.order_id.id),
                                                                      ('product_id.id', '=', line.product_id.id),
                                                                      ('price_unit', '=', line.price_unit),
                                                                      ('product_uom.id', '=', line.product_uom.id),
                                                                      ('custom_discount_type', '=', line.custom_discount_type),
                                                                      ('custom_discount_rate', '=', line.custom_discount_rate),
                                                                  ])


                if len(order_lines) > 1:
                    self._cr.execute('''select product_uom_qty from sale_order_line where id=%s''' % (order_lines[0].id))
                    order_lines_qty = [x[0] for x in self.env.cr.fetchall()]
                    total_qty = order_lines[1].product_qty + order_lines_qty[0]

                    self._cr.execute('''update sale_order_line set product_uom_qty = %s where id=%s''' % (total_qty, order_lines[0].id))
                    self._cr.commit()
                    self._cr.execute('''delete from sale_order_line where id=%s''' % (order_lines[1].id))
                    self._cr.commit()


