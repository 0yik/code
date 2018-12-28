# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
class manufacturing_plan(models.Model):
    _name = 'mrp.plan'
    _inherit = ['mail.thread']
    _description = 'Simple Stock In'

    name = fields.Text('Manufacturing Plan', required=True)
    date = fields.Date('Date')
    mrp_order_ids = fields.One2many('mrp.order', 'mrp_plan_id', 'Manufacturing Orders')
    state = fields.Selection([
        ('draft','Draft'),
        ('confirm','Confirmed'),
        ('cancel','Cancelled')
    ], default='draft')
    add_id = fields.Many2one('mrp.order.wizard')

    @api.multi
    def button_confirm(self):
        self.state = 'confirm'

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'

    @api.multi
    def button_add_mrp_order(self):
        return {
            'name': 'Add Manufacturing Order',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.order.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('manufacturing_plan.mrp_order_wizard_view').id,
            'res_id': self.add_id.id or False,
            'target' : 'new'
        }
class add_mrp_order_wizard(models.Model):
    _name = 'mrp.order.wizard'

    line_ids = fields.One2many('mrp.order.wizard.line', 'add_id')

    @api.model
    def create(self, vals):
        res = super(add_mrp_order_wizard, self).create(vals)
        if res:
            if self._context.get('active_id', False):
                mrp_plan = self.env['mrp.plan'].browse(self._context.get('active_id'))
                mrp_plan.add_id = res.id
        return res

    def create_mrp_production_rescursive(self, move_raw_id):
        if self._context.get('active_id', False):
            mrp_plan = self.env['mrp.plan'].browse(self._context.get('active_id'))
            MRP_PRDODUCTION = self.env['mrp.production']
            MRP_ORDER = self.env['mrp.order']
            product = move_raw_id.product_id
            product_uom_qty = move_raw_id.product_uom_qty
            if product.bom_ids:
                mrp_production_created_id = MRP_PRDODUCTION.create({
                    'mrp_plan_id': mrp_plan.id,
                    'product_id': product.id,
                    'product_qty': product_uom_qty,
                    'bom_id': product.bom_ids[0].id,
                    'date_planned_start': datetime.now().strftime('%Y-%m-%d'),
                    'user_id': self._uid,
                    'product_uom_id': product.uom_id.id,
                    'routing_id': product.bom_ids[0].routing_id and product.bom_ids[0].routing_id.id or False,
                })
                MRP_ORDER.create({
                    'mrp_plan_id': mrp_plan.id,
                    'mrp_production_id': mrp_production_created_id.id,
                })
                if mrp_production_created_id.move_raw_ids:
                    for move_raw_id in mrp_production_created_id.move_raw_ids:
                        self.create_mrp_production_rescursive(move_raw_id)
    @api.multi
    def confirm(self):
        if self._context.get('active_id', False):
            mrp_plan = self.env['mrp.plan'].browse(self._context.get('active_id'))
            MRP_PRDODUCTION = self.env['mrp.production']
            MRP_ORDER = self.env['mrp.order']
            for line in self.line_ids:
                product = line.product_id
                qty = line.quantity
                # product_tmp = product.product_tmp_id
                if product.bom_ids:
                    mrp_production_created_id = MRP_PRDODUCTION.create({
                        'mrp_plan_id': mrp_plan.id,
                        'product_id': product.id,
                        'product_qty': qty,
                        'bom_id': product.bom_ids[0].id,
                        'date_planned_start': datetime.now().strftime('%Y-%m-%d'),
                        'user_id': self._uid,
                        'product_uom_id': product.uom_id.id,
                        'routing_id': product.bom_ids[0].routing_id and product.bom_ids[0].routing_id.id or False,
                    })
                    MRP_ORDER.create({
                        'mrp_plan_id': mrp_plan.id,
                        'mrp_production_id': mrp_production_created_id.id,
                    })
                    if mrp_production_created_id.move_raw_ids:
                        for move_raw_id in mrp_production_created_id.move_raw_ids:
                            self.create_mrp_production_rescursive(move_raw_id)


class add_mrp_order_wizard_line(models.Model):
    _name = 'mrp.order.wizard.line'

    add_id = fields.Many2one('mrp.order.wizard')
    product_id = fields.Many2one('product.product', "Product")
    quantity = fields.Integer('Quantity')
    contract_id = fields.Many2one('account.analytic.account')








class manufacturing_production(models.Model):
    _inherit = 'mrp.production'

    employee_involve_ids = fields.One2many('employee.involve', 'mrp_production_id')
    mrp_plan_id = fields.Many2one('mrp.plan', compute='_compute_plan_id')
    mrp_order_ids = fields.One2many('mrp.order', 'mrp_production_id')

    @api.depends('mrp_order_ids')
    @api.multi
    def _compute_plan_id(self):
        for rec in self:
            if rec.mrp_order_ids:
                rec.mrp_plan_id = rec.mrp_order_ids[0].mrp_plan_id

    @api.multi
    def post_inventory(self):
        super(manufacturing_production, self).post_inventory()
        addition_cost = 0
        for order in self:
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state in ('done'))
            for move in moves_to_finish:
                for line in order.employee_involve_ids:
                    addition_cost += (line.no_of_employees * (
                    line.average_pay / 100) * line.involvement) / order.product_qty
                move.quant_ids.sudo().write({'addition_cost': addition_cost})
            move_to_do_done = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            for move in move_to_do_done:
                move.quant_ids.sudo().write({'addition_cost': addition_cost})
        return True

class employee_involve(models.Model):
    _name = 'employee.involve'

    name = fields.Char(default=" ")
    no_of_employees = fields.Integer('No. of Employees')
    average_pay = fields.Float('Average Cost')
    involvement = fields.Float('Involvement')
    mrp_production_id = fields.Many2one('mrp.production')

class manufacturing_order(models.Model):
    _name = 'mrp.order'

    name = fields.Char('Descriptions', related='mrp_production_id.name')
    mrp_plan_id = fields.Many2one('mrp.plan')
    mrp_production_id = fields.Many2one('mrp.production', "Manufacturing Order")
    product_id = fields.Many2one('product.product', "Product", related='mrp_production_id.product_id')
    date_planned_start = fields.Datetime('Deadline Start', related='mrp_production_id.date_planned_start')
    state = fields.Selection([
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',related='mrp_production_id.state')

class account_move(models.Model):
    _inherit = 'account.move'

    addition_cost = fields.Float('Additional Cost ')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  track_visibility='onchange')

class stock_move(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        if self._context.get('force_valuation_amount'):
            valuation_amount = self._context.get('force_valuation_amount')
        else:
            if self.product_id.cost_method == 'average':
                valuation_amount = cost if self.location_id.usage == 'supplier' and self.location_dest_id.usage == 'internal' else self.product_id.standard_price
            else:
                valuation_amount = cost if self.product_id.cost_method == 'real' else self.product_id.standard_price
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(valuation_amount * qty)
        mrp_production = self.production_id
        addition_cost = 0
        for line in mrp_production.employee_involve_ids:
            addition_cost += (line.no_of_employees * (line.average_pay / 100) * line.involvement) / mrp_production.product_qty
        # check that all data is correct
        debit_value += addition_cost
        if self.company_id.currency_id.is_zero(debit_value):
            if self.product_id.cost_method == 'standard':
                raise UserError(_("The found valuation amount for product %s is zero. Which means there is probably a configuration error. Check the costing method and the standard price") % (self.product_id.name,))
            return []
        credit_value = debit_value

        if self.product_id.cost_method == 'average' and self.company_id.anglo_saxon_accounting:
            # in case of a supplier return in anglo saxon mode, for products in average costing method, the stock_input
            # account books the real purchase price, while the stock account books the average price. The difference is
            # booked in the dedicated price difference account.
            if self.location_dest_id.usage == 'supplier' and self.origin_returned_move_id and self.origin_returned_move_id.purchase_line_id:
                debit_value = self.origin_returned_move_id.price_unit * qty
            # in case of a customer return in anglo saxon mode, for products in average costing method, the stock valuation
            # is made using the original average price to negate the delivery effect.
            if self.location_id.usage == 'customer' and self.origin_returned_move_id:
                debit_value = self.origin_returned_move_id.price_unit * qty
                credit_value = debit_value
        partner_id = (self.picking_id.partner_id and self.env['res.partner']._find_accounting_partner(self.picking_id.partner_id).id) or False
        debit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.picking_id.name,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
        }
        credit_line_vals = {
            'name': self.name,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.picking_id.name,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
        }
        res = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference
            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))
            price_diff_line = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': self.picking_id.name,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
            }
            res.append((0, 0, price_diff_line))
        return res

class stock_quant(models.Model):
    _inherit = 'stock.quant'

    addition_cost = fields.Float('Additional Cost ')

    @api.multi
    def _compute_inventory_value(self):
        for quant in self:
            if quant.company_id != self.env.user.company_id:
                quant = quant.with_context(force_company=quant.company_id.id)
            quant.inventory_value = quant.product_id.standard_price * quant.qty + quant.addition_cost or 0



