# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
import json

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_orders_session_today(self, session_id):
        session = self.env['pos.session'].browse(session_id)
        if session:
            poses = self.env['pos.config'].search([('bus_id.id', '=', session.config_id.bus_id.id), ('order_station', '=', False), ('screen_type', '=', 'waiter')])
            poses_list = []
            grand_total = 0
            for pos in poses:
                sessions = self.env['pos.session'].search([('config_id.id', '=', pos.id)])
                tax_ids = []
                tax_names = []
                taxes = {}
                tax = 0
                total = 0
                s_total = 0
                product_ids = []
                order_lines = {}
                payment_ids = []
                payments = {}
                for session in sessions:
                    pos_orders = self.env['pos.order'].search([('state', '=', 'paid'), ('session_id', '=', session.id), ('date_order', '>=', datetime.now().strftime('%Y-%m-%d 00:00:00'))])
                    for pos_order in pos_orders:
                        for line in pos_order.lines:
                            for line_tax in line.tax_ids:
                                if line_tax.id not in tax_ids:
                                    tax_names.append({ 'name' : line_tax.name, 'id' : line_tax.id})
                                    tax_ids.append(line_tax.id)
                                    taxes[line_tax.id] = 0
                                taxes[line_tax.id] += line.price_subtotal*line_tax.amount/100
                                tax += line.price_subtotal*line_tax.amount/100
                            if line.product_id.id not in product_ids:
                                product_ids.append(line.product_id.id)
                                order_lines[line.product_id.id] = {
                                'product_id': line.product_id.id,
                                'product_name': line.product_id.name,
                                'qty': 0,
                                'price': 0,
                                'total': 0,
                                'tax': 0,
                            }
                            order_lines[line.product_id.id]['qty'] += line.qty
                            order_lines[line.product_id.id]['price'] += line.price_subtotal
                            order_lines[line.product_id.id]['total'] += line.price_subtotal_incl
                            order_lines[line.product_id.id]['tax'] += line.price_subtotal_incl - line.price_subtotal
                        for line in pos_order.statement_ids:
                            if line.journal_id.id not in payment_ids:
                                payment_ids.append(line.journal_id.id)
                                payments[line.journal_id.id] = {
                                    'name': line.journal_id.name,
                                    'amount': 0
                                }
                            payments[line.journal_id.id]['amount'] += line.amount

                        total += pos_order.amount_total - pos_order.amount_tax
                        grand_total += pos_order.amount_total
                        s_total += pos_order.amount_total

                poses_list.append({
                    'name': pos.name,
                    'order_lines': order_lines,
                    'product_ids': product_ids,
                    'payments': payments,
                    'payment_ids': payment_ids,
                    'tax_ids': tax_ids,
                    'taxes': taxes,
                    'tax_names': tax_names,
                    'tax': tax,
                    'total': total,
                    's_total': s_total,
                })

            return {
                'poses': poses_list,
                'grand_total': grand_total,
            }

        else:
            return {
                'pos_orders': [],
                'tax_ids': [],
                'taxes': {},
                'tax_names': [],
                'tax': 0,
                'total': 0,
                'grand_total': 0,
                'session': '',
            }
            # pos_orders = self.env['pos.order'].search(
            #     [('state', '=', 'paid'), ('date_order', '>=', datetime.now().date())])
            # return pos_orders