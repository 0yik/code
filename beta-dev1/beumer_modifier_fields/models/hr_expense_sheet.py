from odoo import models, fields, api,_
from odoo import SUPERUSER_ID
from odoo.exceptions import Warning



class hr_expense_sheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection([
        ('submit', 'To Submit'),
        ('submited', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Rejected')
        ], string='Status')

    @api.model
    def compute_country(self):
        country_id = self.env['res.country'].search([('code','=','SG')])
        return country_id

    check_user_show_approve = fields.Boolean(compute='_check_user_show_approve',default=False)
    country_id              = fields.Many2one('res.country', 'Country', default=compute_country)



    def _check_user_show_approve(self):
        user_ids = []
        group_ids = self.env['res.groups'].search([('name','in',('HR Manager','CFO'))])
        for group_id in group_ids:
            if group_id.users:
                for user in group_id.users:
                    user_ids.append(user.id)
        if self._uid in user_ids:
            self.check_user_show_approve = True
        else:
            self.check_user_show_approve = False

    def _check_user_is_hr_manager(self):
        user_ids = []
        group_ids = self.env['res.groups'].search([('name','=','CFO')])
        for group_id in group_ids:
            if group_id.users:
                for user in group_id.users:
                    if user.id != SUPERUSER_ID:
                        user_ids.append(user.id)
        if self._uid in user_ids:
            return True
        else:
            return False

    @api.model
    def fields_view_get(self,view_id=None, view_type='form',toolbar=False, submenu=False):
        res = super(hr_expense_sheet, self).fields_view_get(view_id, view_type, toolbar=toolbar,submenu=False)
        if view_type != 'form':
            if view_type == 'tree':
                check_user = self._check_user_is_hr_manager()
                if check_user == True:
                    if 'arch' in res:
                        data = res.get('arch').split('\n')
                        modify_edit_str = 'create="0" delete="0"'

                        arch_data = '<tree string="Expense Reports" decoration-warning="state==\'draft\'" decoration-bf="message_unread == True" %s>' % (modify_edit_str)
                        for n in range(1, len(data)):
                            arch_data += '\n%s' % (data[n])
                        res['arch'] = arch_data
                return res
            else:
                return res
        if view_type == 'form':
            check_user = self._check_user_is_hr_manager()
            if check_user == True:
                if 'arch' in res:
                    data = res.get('arch').split('\n')
                    modify_edit_str = 'edit="0" create="0" copy="0" delete="0"'

                    arch_data = '<form string="Expense Reports" class="o_expense_sheet" %s>' % (modify_edit_str)
                    for n in range(1,len(data)):
                        arch_data += '\n%s' % (data[n])
                    res['arch'] = arch_data
            return res

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'submit':
                raise Warning(_("You can't delete record with status %s")%(record.state))
        res = super(hr_expense_sheet, self).unlink()
        return res

    @api.multi
    def copy(self, default={}):
        for record in self:
            if record.state != 'submit':
                raise Warning(_("You can't duplicate record with status %s")%(record.state))
        res = super(hr_expense_sheet, self).copy(default)
        return res

