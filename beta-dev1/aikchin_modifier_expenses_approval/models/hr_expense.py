# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError

class HrExpenseSheet(models.Model):
	_inherit = 'hr.expense.sheet'
	
	@api.multi
	def approve_expense_sheets(self):
    		if not self.user_has_groups('hr_expense.group_hr_expense_user'):
	     		raise UserError(_("Only HR Officers can approve expenses"))
		if not self.user_has_groups("aikchin_modifier_access_right.hr_manager_group"):
			if self.employee_id.parent_id.user_id !=  self.env.user and self._uid != SUPERUSER_ID:
				raise UserError(_("You can't aprrove expenses"))
		self.write({'state': 'approve', 'responsible_id': self.env.user.id})

