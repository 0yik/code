# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from openerp import models, fields, api, _, tools
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp

class ContractVendorAttendees(models.Model):
    _name = 'contract.vendor.attendees'

    vendor_type = fields.Many2one('vendor.type', string='Job')
    partner_ids = fields.Many2many('res.partner', string='Person in charge')
    contract_id = fields.Many2one('account.analytic.account')


class AccountAnalyticAccount(models.Model):
	_inherit= 'account.analytic.account'

	contract_vendor_attendees_ids = fields.One2many('contract.vendor.attendees', 'contract_id', string='Contract Vendor Attendees')

	@api.multi
	def action_validate(self):
		res = super(AccountAnalyticAccount, self).action_validate()
		for line in self.account_analytic_account_line_id:
			if line.product_id and line.product_id.milestone_tmpl_id:
				for milestone_line in line.product_id.milestone_tmpl_id.milestone_lines:
					if milestone_line.milestone_id:
						new_milestone_id = milestone_line.milestone_id.copy()
						new_milestone_id.is_tmpl = False
						new_milestone_id.contract_id = self.id
						for line in milestone_line.milestone_id.milestone_vendor_ids:
							vals = {
							'vendor_id': line.vendor_id.id,
							'milestone_id': new_milestone_id.id,
							'check_intime': line.check_intime,
							'vendor_type': line.vendor_type.id,
							'service_charged': [(6, 0, line.service_charged.ids)],
							}
							self.env['milestone.vendors'].create(vals)
						# new_milestone_id.milestone_vendor_ids = milestone_line.milestone_id.milestone_vendor_ids
						if milestone_line.milestone_id.bridal_specialist:
							if milestone_line.milestone_id.bridal_specialist.work_email:
								template_id = self.env.ref('tgw_project_milestone.milestone_bridal_specialist_template_id')
								template_id.sudo().email_to = milestone_line.milestone_id.bridal_specialist.work_email
								template_id.sudo().email_from = ''
								template_id.sudo().send_mail(milestone_line.milestone_id.id, force_send=True)
						contract_booking_id = self.env['milestone.contract.bookings'].create({
							'milestone_id': milestone_line.milestone_id.id,
							'account_analytic_account_id':self.id,
							'partner_id':self.partner_id.id,
							})
						if new_milestone_id:
							new_milestone_id.milestone_contract_bookings_id = contract_booking_id.id
						if milestone_line.milestone_id.involve_vendor:
							for milestone_vendor in milestone_line.milestone_id.milestone_vendor_ids:
								self.env['contract.vendor.attendees'].create({
									'vendor_type':milestone_vendor.vendor_type.id,
									'partner_ids':[(6,0,milestone_vendor.vendor_id.ids)],
									'contract_id':self.id,
									})
		return res

class MilestoneContractBookings(models.Model):
    _inherit = 'milestone.contract.bookings'

    @api.multi
    def write(self, vals):
    	if vals.get('date'):
	    	res = super(MilestoneContractBookings, self).write(vals)
	    	milestone_id = self.env['milestone.milestone'].search([('milestone_contract_bookings_id','=',self.id)], limit=1)
	    	if milestone_id:
	    		milestone_id.due_date = vals.get('date')
    	return res