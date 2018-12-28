# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit= "pos.order"

    all_free = fields.Boolean('Apply All Free?')

    state = fields.Selection(
        [('draft', 'New'),('open','Open'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'), ('invoiced', 'Invoiced')],
        'Status', readonly=True, copy=False, default='draft')

    @api.multi
    def confirmed_email(self):
        for item in self:
            item.state = 'open'

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        super(PosOrder, self)._compute_amount_all()
        for order in self:
            if order.all_free:
                order.amount_tax = 0
                order.amount_total = 0

    @api.model
    def _process_order(self, pos_order):
        if pos_order.get('popup_option') == 'Staff Meal':
            if pos_order.get('statement_ids'):
                statement = pos_order.get('statement_ids')
                statement[0][2]['account_id'] = False
                statement[0][2]['statement_id'] = self.env.ref('staff_meal.account_bank_statement_temp').id
                pos_order['statement_ids'] = statement
        order = super(PosOrder, self)._process_order(pos_order)
        # if pos_order.get('popup_option') == 'Staff Meal':
        #     if order.statement_ids:
        #         for payment in order.statement_ids:
        #             payment.amount = 0
        return order

    @api.model
    def get_list_payment_confirm(self):
        orders = self.env['pos.order'].search([('state', '=', 'open')],limit=100)
        result = []
        for order in orders:
            result.append(order.convert_to_json())
        return result

    @api.model
    def paid_order_open(self,id):
        order = self.browse(int(id))
        order.state = 'paid'

    @api.model
    def convert_to_json(self):
        return {
            'id': self.id,
            'name' : self.name,
            'branch': self.branch_id.name,
            'oder_date': self.date_order,
            'customer_count': self.customer_count,
            'all_free' : self.all_free,
            'note' : self.note,
        }

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['all_free'] = ui_order.get('all_free')
        res['note'] = ui_order.get('note')
        return res

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def _order_line_fields(self, line):
        fields_return = super(PosOrderLine, self)._order_line_fields(line)
        if(fields_return[2].get('popup_option') == 'Staff Meal'):
            fields_return[2].update({'price_unit': 0})
        return fields_return

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    compute_amount = fields.Monetary(string='Amount',compute = '_compute_amount',digits=0)

    @api.multi
    def _compute_amount(self):
        for item in self:
            if item.statement_id.name == 'staff meal':
                item.compute_amount = 0
            else:
                item.compute_amount = item.amount
