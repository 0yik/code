# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models
from odoo import api, fields, models
# Empty class but required since it's overridden by sale & crm
class FundConfigSettings(models.TransientModel):

	_name = 'fund.config.settings'
	_inherit = 'res.config.settings'

	group_use_journal = fields.Selection([
		('posted', "Proceed as Posted"),
		('draft', "Proceed as Draft")
	], string="journal Setting")


	@api.model 
	def get_default_group_use_journal(self, fields): 
		fund_obj = self.env['fund.config.settings'].search([])
		if fund_obj:
			return {'group_use_journal': fund_obj[-1].group_use_journal} 
		else:
			return {'group_use_journal':False}