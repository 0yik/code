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

class crm_lead(models.Model):
	_inherit = "crm.lead"

	contrac_count = fields.Integer("Contracts", compute='_compute_contracts_count')

	@api.multi
	def _compute_contracts_count(self):
		if self:
			for partner in self:
				partner.contrac_count = self.env['account.analytic.account'].search_count([('partner_id','=',partner.partner_id.id)])


class account_analytic_account(models.Model):
	_inherit = "account.analytic.account"

	opportunity_id = fields.Many2one('crm.lead','Opportunity')

	@api.model
	def create(self, vals):
		res = super(account_analytic_account, self).create(vals)
		if self._context.get('active_model') == 'crm.lead' and self._context.get('active_id'):
			lead_obj = self.env['crm.lead'].browse(self._context.get('active_id'))
			lead_obj.action_set_won()
		return res

	@api.multi
	def set_open(self):
		for cont in self:
			stage_id = self.opportunity_id._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
			self.opportunity_id.write({'stage_id': stage_id.id, 'probability': 100})
			self.partner_id.write({'customer':True,'opportunity_partner':False})
		return self.write({'state': 'open'})