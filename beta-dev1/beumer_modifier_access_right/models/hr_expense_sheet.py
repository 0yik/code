from odoo import models, fields, api

class accouting_customer(models.Model):
    _inherit = 'hr.expense.sheet'

    # def _check_user_ap(self):
    #     user_id = self.env['res.users'].browse(self._uid)
    #     if user_id:
    #         if user_id.login == 'ap_manager':
    #             return True
    #         else:
    #             return False
    # def _check_user_ar(self):
    #     user_id = self.env['res.users'].browse(self._uid)
    #     if user_id:
    #         if user_id.login == 'ar_manager':
    #             return True
    #         else:
    #             return False

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(accouting_customer, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
    #     hr_sheet = self.env.ref('hr_expense.action_hr_expense_sheet_my_all').id
    #     if self._context.get('params') and self._context.get('params').get('action') and hr_sheet == self._context.get('params').get('action'):
    #         if view_type == 'form':
    #                 # if 'arch' in res:
    #                 #     data = res.get('arch').split('\n')
    #                 #     modify_edit_str = 'edit="0" create="0" copy="0" delete="0"'
    #                 #
    #                 #     arch_data = '<form %s>' % (modify_edit_str)
    #                 #     for n in range(1, len(data)):
    #                 #         arch_data += '\n%s' % (data[n])
    #                 #     res['arch'] = arch_data
    #             return res
    #
    #     else:
    #         return res