# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError
class arf_modifer_crmhomepage(models.Model):
	_inherit = 'res.partner'

	nric_fin    = fields.Char(string='NRIC/FIN')
	passport_no = fields.Char(string='Passport No')
	roc_no      = fields.Char(string='ROC No')

	home = fields.Char('home')
	work = fields.Char('work')

	@api.model
	def create(self,vals):
		if vals['mobile']==False and vals['home']==False and vals['work']==False:
			raise UserError(("Please enter mobile, home or work"))
		return super(arf_modifer_crmhomepage, self).create(vals)
