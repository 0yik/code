from odoo import api, fields, models, tools, SUPERUSER_ID, _


class ChangePasswordWizard(models.TransientModel):

    _inherit = "change.password.wizard"

    @api.multi
    def change_password_button(self):
        res = super(ChangePasswordWizard, self).change_password_button()
#         if self._context.get('from_partner'):
#             compose_form_id = self.env['ir.model.data'].sudo().get_object_reference('hilti_reusable_user_respartner_changepassword', 'view_my_profile_form')[1]
#             ctx = dict()
#             ctx.update({
#                 'active_model': 'res.partrner',
#                 'active_id': self._context.get('partner_id'),
#                 'active_ids': [self._context.get('partner_id')],
#             })
#             return {
#                 'type': 'ir.actions.act_window',
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_model': 'res.partner',
#                 'views': [(compose_form_id, 'form')],
#                 'view_id': compose_form_id,
#                 'res_id': self._context.get('partner_id'),
#                 'target': 'new',
#                 'context': ctx,
#             }
        return res


class res_partner(models.Model):

    _inherit = "res.partner"
    
    @api.one
    def _compute_user(self):
        self.res_user_id = self.env['res.users'].search([('partner_id', '=', self.id)])

    equipment_ids = fields.Many2many('equipment.equipment', string='Equipments')
    res_user_id = fields.Many2one('res.users', 'User', compute='_compute_user', store=True)
    
    @api.multi
    def change_password(self):
        compose_form_id = self.env['ir.model.data'].sudo().get_object_reference('base', 'change_password_wizard_view')[1]
        ctx = dict()
        ctx.update({
            'active_model': 'res.users',
            'active_id': self.res_user_id.id,
            'active_ids': [self.res_user_id.id],
            'from_partner': True,
            'partner_id': self.id
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'change.password.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }