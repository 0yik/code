# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class SaleOrder(models.Model):
	_inherit = 'sale.order'
	
	@api.model
    	def create(self, vals):
		res = super(SaleOrder, self).create(vals)
		seq = res.name
		name = seq.split('-')
		today=datetime.datetime.today().strftime("%m/%d/%Y")
		date = today[:-5][3:]
		today=today[-2:]+date
		branch_abbr = self.env['res.branch'].browse(vals['branch_id'])
		if branch_abbr.abbreviation:
			res.name = ('%s/%s/%s %s') %(name[0],branch_abbr.abbreviation,today,name[1][1:])
		else:
			res.name = ('%s/%s %s') %(name[0],today,name[1][1:])
		return res

	@api.multi
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		seq = self.name
		seq = seq.split('-')
		today=datetime.datetime.today().strftime("%m/%d/%Y")
		date = today[:-5][3:]
		today=today[-2:]+date
		if self.branch_id.abbreviation:
			self.name = ('%s/%s/%s %s') %(seq[0],self.branch_id.abbreviation,today,seq[1][1:])
		else:
			self.name = ('%s/%s %s') %(seq[0],today,seq[1][1:])
		return res
