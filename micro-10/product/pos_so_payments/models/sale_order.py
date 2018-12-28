# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    deliver_id = fields.Many2one('hr.employee', string="Delivered by")

class sales_order(models.Model):
    _inherit = 'sale.order'

    origin = fields.Char("Origin")
    is_paid = fields.Boolean('Is paid', default=False)
    is_delivery = fields.Boolean('Is Delivery', default=False)

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
                context = {"active_model": 'sale.order', "active_ids": [record.id], "active_id": record.id}
                # Now I create invoice.
                payment = self.env['sale.advance.payment.inv'].create({
                    'advance_payment_method': 'all'
                })
                invoice_list = []
                payment.with_context(context).create_invoices()
                if record.invoice_ids:
                    record.invoice_status = 'invoiced'
                    record.invoice_ids.action_invoice_open()
                    record.is_delivery = True
                    for invoice in record.invoice_ids:
                        invoice_list.append({
                            'id': invoice.id,
                            'partner_id': invoice.partner_id.name,
                            'date_invoice': invoice.date_invoice,
                            'amount_total': invoice.amount_total,
                        })
                return invoice_list

            except Exception as e:
                record.invoice_status = 'invoiced'
                record.is_delivery = True
                print e
                return []

    def create_invoice(self):
        try:
            context = {"active_model": 'sale.order', "active_ids": [self.id], "active_id": self.id}
            # Now I create invoice.
            payment = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method': 'all'
            })
            payment.with_context(context).create_invoices()
            if self.invoice_ids:
                self.invoice_status = 'invoiced'
                self.invoice_ids.action_invoice_open()
        except Exception as e:
            print e

class PosSalesOrder(models.Model):
    _inherit = "pos.sales.order"
    _description = "Create a sale order through point of sale for home delivery"

    @api.model
    def create_pos_sale_order(self, ui_order, note, cashier, client_fields, exp_date):
        res = super(PosSalesOrder, self).create_pos_sale_order(ui_order, note, cashier, client_fields, exp_date)
        sales_order_id = res.get('id', False)
        if sales_order_id:
            sales_order = self.env['sale.order'].browse(res['id'])
            sales_order.write({
                'origin' : "Point of sale"
            })
        return res

class account_account(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def payment_invoice(self, journal_id, payment_amount, payment_date):
        # Register partial payment
        try:
            journal = self.env['account.journal'].browse(int(journal_id))
            payment = self.env['account.payment'].create({
                'invoice_ids': [(4, inv.id, None) for inv in self],
                'amount': payment_amount,
                'currency_id': self.currency_id.id,
                'payment_date': payment_date,
                'communication': 'Point of sale',
                'partner_id': self.mapped('partner_id')[0].id,
                'partner_type': 'customer',
                'journal_id': journal.id,
                'payment_type': 'inbound',
                'payment_method_id': journal.inbound_payment_method_ids[0].id,
                'payment_difference_handling': 'open',
                'writeoff_account_id': False,
            })
            payment.post()
            return {
                'status': True,
                'message': "Payment successfully",
            }
        except Exception as e:
            print e
            return {
                'status' : False,
                'message' : "Payment failed",
            }

