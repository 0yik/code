# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
	_inherit = 'payment.transaction'

	student_id = fields.Many2one('student.student')

	@api.multi
	def write(self, vals):
		if vals.get('state',False) and (self.student_id or vals.get('student_id',False)):
			if vals.get('state') == 'done':
				student_payslip_id = self.env['student.payslip'].sudo().search([('student_id','=',self.student_id.id)], limit=1)
				if student_payslip_id and not student_payslip_id.journal_id:
					journal = self.env['account.journal'].sudo().search([('type', '=',
																'sale')],
															  limit=1)
					student_payslip_id.journal_id = journal and journal.id
				if self.student_id and self.student_id.school_id and self.student_id.school_id.application_fee_id:
					if student_payslip_id and not student_payslip_id.fees_structure_id:
						student_payslip_id.fees_structure_id = self.student_id.school_id.application_fee_id.id
				template_id = self.env.ref('online_school_enrollment.student_payment_confirmation_template_id')
				template_id.email_to = self.student_id.email
				template_id.send_mail(self.student_id.id, force_send=True)
			  	student_payslip_id.onchange_student()
				student_payslip_id.onchange_journal_id()
				student_payslip_id.payslip_confirm()
				student_payslip_id.student_pay_fees()
				student_payslip_id.payslip_paid()
		res = super(PaymentTransaction, self).write(vals)
		return res
