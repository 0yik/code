# -*- coding: utf-8 -*-

from odoo import models, fields


class Repair(models.Model):
	_inherit = 'mrp.repair'

	asset_id = fields.Many2one("account.asset.asset", "Asset")
	maintenance_id = fields.Many2one("maintenance.request", "Maintenance No")
	product_id = fields.Many2one("product.product", required=False)

	def write(self, vals):
		res = super(Repair, self).write(vals)
		if vals.get('state') == 'done':
			stage_repaired = self.env['maintenance.stage'].search([('name', 'ilike', 'repaired')])
			if stage_repaired:
				self.mapped('maintenance_id').write({'stage_id': stage_repaired.id})
		return res
