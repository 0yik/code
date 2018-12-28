# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.misc import ustr
from ast import literal_eval
from odoo.addons.auth_signup.models.res_users import SignupError


class res_users(models.Model):
    _inherit = 'res.users'
    
    account_number = fields.Char(string="Account Number")
    
    @api.model
    def create(self, vals):
        result = super(res_users, self).create(vals)
        if result:
            result.partner_id.account_number = result.account_number
        return result
    
    @api.multi
    def verify_customer(self):
        self.write({
            'active': True
        })
        return self.env.ref('hilti_modifier_loginsignup.action_res_users_inactive').read()[0]
        
        
#         form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_modifier_loginsignup', 'view_inactive_users_tree')[1]
#         return {
#                 'name': 'Customer Verification',
#                 'type': 'ir.actions.act_window',
#                 'view_type': 'form',
#                 'view_mode': 'tree,form',
#                 'res_model': 'res.users',
#                 'domain': [('active', '=', False)],
# #                 'view_ids': [
# #                     (5, 0, 0),
# #                     (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('view_inactive_users_tree').id}),
# #                     (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('base.view_users_form').id})
# #             ],
#                 'views': [(form_id, 'tree')],
#                 'view_id': form_id,
#                 'target': 'self',
#                 'context': {'customer_verification': True},
#             }
    
    @api.model
    def _signup_create_user(self, values):
        """ create a new user from the template user """
        IrConfigParam = self.env['ir.config_parameter']
        template_user_id = literal_eval(IrConfigParam.get_param('auth_signup.template_user_id', 'False'))
        template_user = self.browse(template_user_id)
        assert template_user.exists(), 'Signup: invalid template user'

        # check that uninvited users may sign up
        if 'partner_id' not in values:
            if not literal_eval(IrConfigParam.get_param('auth_signup.allow_uninvited', 'False')):
                raise SignupError('Signup is not allowed for uninvited users')

        assert values.get('login'), "Signup: no login given for new user"
        assert values.get('partner_id') or values.get('name'), "Signup: no name or partner given for new user"

        # create a copy of the template user (attached to a specific partner_id if given)
        values['active'] = False
        try:
            with self.env.cr.savepoint():
                return template_user.with_context(no_reset_password=True).copy(values)
        except Exception, e:
            # copy may failed if asked login is not available.
            raise SignupError(ustr(e))
    
    
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'customer_verification' in self._context and self._context.get('customer_verification'):
            args.append(['id', 'not in', [self.env.ref('base.default_user').id, self.env.ref('base.public_user').id, self.env.ref('auth_signup.default_template_user').id]])
        return super(res_users, self).search(args, offset, limit, order, count=count)