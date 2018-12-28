# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class MaintenanceRequest(models.Model):
	_inherit = 'maintenance.request'

	asset_id = fields.Many2one("account.asset.asset", "Asset")
	currency_id = fields.Many2one("res.currency", "Currency")
	cost = fields.Float("Cost")

	def btn_start_maintenance(self):
		self.ensure_one()
		if not self.stage_id.done:
			if self.stage_id.name.lower() == "in progress":
				raise UserError(_("Maintenance Request is already in IN PROGRESS stage."))

			stage_inprogress = self.env['maintenance.stage'].search([('name', 'ilike', 'in progress')], limit=1)
			if stage_inprogress:
				self.stage_id = stage_inprogress
			else:
				raise UserError(_("IN PROGRESS stage is not found."))
		else:
			raise UserError(_("Maintenance Request is already proceeded."))

	def write(self, vals):
		MrpRepair = self.env['mrp.repair']
		res = super(MaintenanceRequest, self).write(vals)
		if 'stage_id' in vals and self and self[0].stage_id.name.lower() == 'in progress':
			location_id = MrpRepair._default_stock_location()
			for request in self.filtered(lambda r: r.maintenance_type == 'corrective'):
				repair = MrpRepair.create({'maintenance_id': request.id, 'location_dest_id': location_id})
		return res
