from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class res_branch(models.Model):
	_inherit = 'res.branch'

	branch = fields.Char(string='Branch ID', required=True)

	@api.constrains('branch')
	def _check_branch_duplicate(self):
		for record in self:
			branch_names = self.search([('id','!=',self.id)]);
			for branch_name in branch_names:
				if str(branch_name.branch).lower() == str(record.branch).lower():
					raise ValidationError(_('Error ! Branch is already created.'))

class res_company(models.Model):
	_inherit = 'res.company'

	def reflect_code_prefix_change(self, old_code, new_code, digits):
		accounts = self.env['account.account'].search([('code', 'like', old_code), ('internal_type', '=', 'liquidity'),
													   ('company_id', '=', self.id)], order='code asc')
		for account in accounts:
			check_accounts = self.env['account.account'].search(
				[('code', '=', self.get_new_account_code(account.code, old_code, new_code, digits)),
				 ('company_id', '=', self.id)])
			if account.code.startswith(old_code) and not check_accounts:
				account.write({'code': self.get_new_account_code(account.code, old_code, new_code, digits)})
	
