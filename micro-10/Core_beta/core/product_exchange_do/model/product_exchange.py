# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.osv.orm import setup_modifiers
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp

class stock_picking(models.Model):
	_inherit = 'stock.picking'

	@api.one
	@api.depends('picking_type_id')
	def get_code(self):
		self.pic_code = self.picking_type_id.code

	pic_code = fields.Char(compute="get_code", string="Picking Code")


	