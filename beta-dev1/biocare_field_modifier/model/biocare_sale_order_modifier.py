# -*- coding: utf-8 -*-
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

class sale_from(models.Model):
	_name = 'sale.from'

	name = fields.Char('Name')

class sale_attention(models.Model):
	_name = 'sale.attention'

	name = fields.Char('Name')

class sale_order(models.Model):
	_inherit = 'sale.order'
	
	project_sale = fields.Char('Project')
	email_sale = fields.Char('Email')
	currency_sale = fields.Many2one('res.currency','Currency')
	from_sale = fields.Many2one('sale.from','From')
	
	prepared_by = fields.Many2one('res.users','Prepared By')
	validated_by = fields.Many2one('res.users', 'Validated By')
	attention_sale = fields.Many2one('sale.attention','Attention')
	terms_sale = fields.Char('Terms')
	