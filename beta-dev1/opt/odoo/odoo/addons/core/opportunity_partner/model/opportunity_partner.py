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

class res_partner(models.Model):
	_inherit = 'res.partner'

	opportunity_partner = fields.Boolean('Opportunity Partner')


class crm_lead(models.Model):
	_inherit = "crm.lead"

	@api.model
	def create(self, vals):
		res = super(crm_lead, self).create(vals)
		context = dict(self._context or {})
		if not vals.get('partner_id',False):
			res_partner = {
				'name':vals.get('name'),
				'email':vals.get('email_from'),
				'phone':vals.get('phone'),
				'function':vals.get('function'),
				'mobile':vals.get('mobile'),
				'fax':vals.get('fax'),
				'street':vals.get('street'),
				'street2':vals.get('street2'),
				'city':vals.get('city'),
				'state_id':vals.get('state_id'),
				'zip':vals.get('zip'),
				'country_id':vals.get('country_id'),
				'title':vals.get('title'),
				'category_id': vals.get('tag_ids'),
				'opportunity_partner':True,
				'customer':False,
				'supplier':False,
				'company_type':'company',
				'is_company':True,
				'type':'contact',
				'user_id':vals.get('user_id'),
			}
			partner_id = self.env['res.partner'].create(res_partner)
			res.write({'partner_id':partner_id.id,'partner_name':vals.get('name')})
		return res
	
	@api.onchange('user_id')
 	def _onchange_user_id(self):
 		""" When changing the user, also set a team_id or restrict team id to the ones user_id is member of. """
  		values = self._onchange_user_values(self.user_id.id)
  		self.partner_id.write({'user_id':self.user_id.id})
  		self.update(values)

# 	@api.multi
# 	def write(self, vals):
# 		if not self.partner_id and not vals.get('partner_id'):
# 			res_partner = {
# 				'name': vals.get('partner_name'),
# 				'email': vals.get('email_from'),
# 				'phone': vals.get('phone'),
# 				'function': vals.get('function'),
# 				'mobile': vals.get('mobile'),
# 				'fax': vals.get('fax'),
# 				'street': vals.get('street'),
# 				'street2': vals.get('street2'),
# 				'city': vals.get('city'),
# 				'state_id': vals.get('state_id'),
# 				'zip': vals.get('zip'),
# 				'country_id': vals.get('country_id'),
# 				'title': vals.get('title'),
# 				'category_id': vals.get('tag_ids'),
# 				'opportunity_partner': True,
# 				'customer': False,
# 				'supplier': False,
# 				'company_type': 'company',
# 				'is_company': True,
# 				'type': 'contact',
# 			}
# 			partner_id = self.env['res.partner'].create(res_partner)
# 			vals.update({'partner_id': partner_id and partner_id.id or False})
# 		return super(crm_lead, self).write(vals)