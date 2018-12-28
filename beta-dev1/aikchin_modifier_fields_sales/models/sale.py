# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class SaleOrder(models.Model):
	_inherit = 'sale.order'
	
	@api.onchange('date_order')
	def _onchnage_date_order(self):
		if self.date_order:
			expiry_date = datetime.strptime(self.date_order, "%Y-%m-%d %H:%M:%S") + timedelta(days=14)
			self.validity_date = expiry_date

	issuer_id = fields.Many2one('hr.employee', 'Issuer')
