# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class PosConfig(models.Model):
	_inherit = 'pos.config'

	session_type = fields.Selection([('cashier', 'Cashier'), ('order', 'Order')])
