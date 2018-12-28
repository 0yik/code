# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class res_partner(models.Model):
	_inherit = 'res.partner'
	
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if self._context.has_key('is_contact'):
			if self._context.has_key('partner_id') and self._context.get('partner_id'):
				res_partner_id = self.env['res.partner'].browse(self._context.get('partner_id'))
				recs = res_partner_id.child_ids
		else:
			recs = self.search([('name', operator, name)] + args, limit=limit)
		return recs.name_get()

