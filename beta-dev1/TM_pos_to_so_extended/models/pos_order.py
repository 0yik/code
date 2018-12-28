import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class pos_order(models.Model):
	_inherit = 'pos.order'

	@api.model
	def create_from_ui(self, orders):
		# inherit origin
		submitted_references = [o['data']['name'] for o in orders]
		pos_order = self.search([('pos_reference', 'in', submitted_references)])
		existing_orders = pos_order.read(['pos_reference'])
		existing_references = set([o['pos_reference'] for o in existing_orders])
		orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
		order_ids = []

		for tmp_order in orders_to_save:
			to_invoice = tmp_order['to_invoice']
			order = tmp_order['data']
			if to_invoice:
				self._match_payment_to_invoice(order)
			pos_order = self._process_order(order)
			order_ids.append(pos_order.id)

			try:
				pos_order.action_pos_order_paid()
			except psycopg2.OperationalError:
				# do not hide transactional errors, the order(s) won't be saved!
				raise
			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

			if to_invoice:
				pos_order.action_pos_order_invoice()
				pos_order.invoice_id.sudo().action_invoice_open()
				pos_order.account_move = pos_order.invoice_id.move_id

		#inherit pos_home_delivery
		for order in order_ids:
			order_rec = self.browse(order)
			ref_order = [o['data'] for o in orders if o['data'].get('name') == order_rec.pos_reference]
			if ref_order:
				to_invoice = all([o['to_invoice'] for o in orders if o['data'].get('name') == order_rec.pos_reference])
				is_delivery = self._check_journal(ref_order[0])
				if is_delivery and not to_invoice:
					order_rec.write({'state': 'done'})
			delivery_ids = self.env['pos.delivery.order'].search([('order_no', '=', order_rec.pos_reference)])
			if delivery_ids:
				delivery_ids.write({'pos_order_id': order})
		#inherit pos_loyalty
		for order in orders:
			if order['data']['loyalty_points'] != 0 and order['data']['partner_id']:
				partner = self.env['res.partner'].sudo().browse(order['data']['partner_id'])
				partner.write({'loyalty_points': partner['loyalty_points'] + order['data']['loyalty_points']})
		#inherit pos_orders
		order_objs = self.env['pos.order'].browse(order_ids)
		result = {}
		order_list = []
		order_line_list = []
		statement_list = []
		for order_obj in order_objs:
			vals = {}
			vals['lines'] = []
			if hasattr(order_objs[0], 'return_status'):
				if not order_obj.is_return_order:
					vals['return_status'] = order_obj.return_status
					vals['existing'] = False
					vals['id'] = order_obj.id
				else:
					order_obj.return_order_id.return_status = order_obj.return_status
					vals['existing'] = True
					vals['id'] = order_obj.id
					vals['original_order_id'] = order_obj.return_order_id.id
					vals['return_status'] = order_obj.return_order_id.return_status
					for line in order_obj.lines:
						line_vals = {}
						line_vals['id'] = line.original_line_id.id
						line_vals['line_qty_returned'] = line.original_line_id.line_qty_returned
						line_vals['existing'] = True
						order_line_list.append(line_vals)
			vals['statement_ids'] = order_obj.statement_ids.ids
			vals['name'] = order_obj.name
			vals['amount_total'] = order_obj.amount_total
			vals['pos_reference'] = order_obj.pos_reference
			vals['date_order'] = order_obj.date_order
			if order_obj.invoice_id:
				vals['invoice_id'] = order_obj.invoice_id.id
			else:
				vals['invoice_id'] = False
			if order_obj.partner_id:
				vals['partner_id'] = [order_obj.partner_id.id, order_obj.partner_id.name]
			else:
				vals['partner_id'] = False
			if (not hasattr(order_objs[0], 'return_status') or (
				hasattr(order_objs[0], 'return_status') and not order_obj.is_return_order)):
				vals['id'] = order_obj.id
				for line in order_obj.lines:
					vals['lines'].append(line.id)
					line_vals = {}
					# LINE DATAA
					line_vals['create_date'] = line.create_date
					line_vals['discount'] = line.discount
					line_vals['display_name'] = line.display_name
					line_vals['id'] = line.id
					line_vals['order_id'] = [line.order_id.id, line.order_id.name]
					line_vals['price_subtotal'] = line.price_subtotal
					line_vals['price_subtotal_incl'] = line.price_subtotal_incl
					line_vals['price_unit'] = line.price_unit
					line_vals['product_id'] = [line.product_id.id, line.product_id.name]
					line_vals['qty'] = line.qty
					line_vals['write_date'] = line.write_date
					if hasattr(line, 'line_qty_returned'):
						line_vals['line_qty_returned'] = line.line_qty_returned
					# LINE DATAA
					order_line_list.append(line_vals)
				for statement_id in order_obj.statement_ids:
					statement_vals = {}
					# STATEMENT DATAA
					statement_vals['amount'] = statement_id.amount
					statement_vals['id'] = statement_id.id
					if statement_id.journal_id:
						currency = statement_id.journal_id.currency_id or statement_id.journal_id.company_id.currency_id
						statement_vals['journal_id'] = [statement_id.journal_id.id,
														statement_id.journal_id.name + " (" + currency.name + ")"]
					else:
						statement_vals['journal_id'] = False
					statement_list.append(statement_vals)
			order_list.append(vals)
		result['orders'] = order_list
		result['orderlines'] = order_line_list
		result['statements'] = statement_list
		return result
