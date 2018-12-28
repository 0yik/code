# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    deliver_id = fields.Many2one('hr.employee', string="Delivered by")

class sales_order(models.Model):
    _inherit = 'sale.order'

    sender_branch_id = fields.Many2one('res.branch', string="Sender Branch")
    payment_plan_id = fields.Many2one('account.journal', string="Payment Plan")
    category         = fields.Selection([('delivery', 'Delivery'), ('transfer_out', 'Transfer out')], 'Category', default = 'delivery')
    is_delivery      = fields.Boolean('Is paid', default=False)

    @api.multi
    def validate_delivery_invoice(self, deliver_id):
        for record in self:
            try:
                for stock_pick in record.picking_ids:
                    try:
                        stock_pick.deliver_id = deliver_id
                        wiz_act = stock_pick.do_new_transfer()
                        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
                        wiz.process()
                    except Exception as e:
                        print e

                # Now I create invoice.
                context = {"active_model": 'sale.order', "active_ids": [record.id], "active_id": record.id}
                payment = self.env['sale.advance.payment.inv'].create({
                    'advance_payment_method': 'all'
                })
                payment.with_context(context).create_invoices()
                if record.invoice_ids:
                    record.invoice_ids.action_invoice_open()
                    record.is_delivery = True
            except Exception as e:
                record.is_delivery = True
                print e

    def create_invoice(self):
        try:
            context = {"active_model": 'sale.order', "active_ids": [self.id], "active_id": self.id}
            # Now I create invoice.
            payment = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method': 'all'
            })
            payment.with_context(context).create_invoices()
            if self.invoice_ids:
                self.invoice_ids.action_invoice_open()
        except Exception as e:
            print e

class PosSalesOrder(models.Model):
    _inherit = "pos.sales.order"
    _description = "Create a sale order through point of sale for home delivery"

    @api.model
    def create_pos_sale_order(self, ui_order, note, cashier, client_fields, exp_date):
        res = super(PosSalesOrder, self).create_pos_sale_order(ui_order, note, cashier, client_fields, exp_date)
        category = ui_order.get('category', False)
        branch_id = ui_order.get('branch_id', False)
        payment_plan_id = ui_order.get('payment_plan_id', False)
        sender_branch_id = ui_order.get('sender_branch_id', False)
        sales_order_id = res.get('id', False)
        if sales_order_id:
            sales_order = self.env['sale.order'].browse(res['id'])
            sales_order.write({
                'branch_id' : branch_id,
                'sender_branch_id' : sender_branch_id,
                'payment_plan_id' : payment_plan_id,
            })
            if category in ['delivery', 'transfer_out']:
                sales_order.write({
                    'category': category,
                })
            if category == 'transfer_out':
                sales_order.action_confirm()
                sales_order.create_invoice()
                if sales_order.invoice_ids:
                    sales_order.invoice_ids.write({'branch_id': sender_branch_id})

        return res


