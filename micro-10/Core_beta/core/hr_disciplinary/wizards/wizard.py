from odoo import models, fields, api

class DisciplinaryWizard(models.TransientModel):
	_name = 'disciplinary.wizard'

	employee=fields.Many2one('hr.employee', string="Employee", required=True)
	disciplined_date=fields.Date(string="Disciplined Date", required=True)
	disciplinary_stages=fields.Many2one('disciplinary.stage', string="Disciplinary Stages", required=True)
	valid_for_months=fields.Integer(string="Valid for (Months)", related="disciplinary_stages.valid_for_months")
	reason_disciplinary=fields.Text(string="Reason of Disciplinary", required=True)
	# manual_action=fields.Text(string="Manual Action", related="disciplinary_stages.action_to_do")
	send_an_email=fields.Boolean(string="Sent an Email", related="disciplinary_stages.send_email")
	# send_a_letter=fields.Boolean(string="Sent a Letter")

	@api.multi
	def allocate_email(self):
		for obj in self:
			vals = {
				"date_diciplined" : obj.disciplined_date,
				"disciplinary_stage" : obj.disciplinary_stage,
				# "valid_until" : obj.va
				"reason_disciplinary" : obj.reason_disciplinary,
				"manual_action" : obj.manual_action,
				"employee_id" : obj.employee.id,
			}
			self.employee.write({'disciplinary_history_ids' : [(0,0, vals)]})
			if obj.send_an_email:
				template = self.env.ref('hr_disciplinary.disciplinary_allocate_mail')
				mail_id = self.env['mail.template'].browse(template.id).send_mail(self.employee.id)
				return self.env['mail.mail'].browse(mail_id).send()