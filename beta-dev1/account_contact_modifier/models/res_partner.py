from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    child_partner_ids = fields.Many2many('res.partner','respartner_point_child_rel','child_id','parent_id',string='',domain="[('is_company','=',1)]")
    # child_ids         = fields.Many2many('res.partner','res_partner_child_id_rel','child_ids','parent_ids')

    @api.multi
    def update_child(self):
        partner_ids = self.env['res.partner'].search([])
        for record in partner_ids:
            record.child_ids = record.child_partner_ids

    # @api.multi
    # def add_button(self):
    #     self.child_partner_ids = self.child_ids
    #     return {
    #         'type'      : 'ir.actions.act_window',
    #         'name'      : 'Customer',
    #         'res_model' : 'res.partner',
    #         'view_id'   : self.env.ref('account_contact_modifier.view_partner_form_children_link').id,
    #         'res_id'    : self.id,
    #         'view_mode' : 'form',
    #         'view_type' : 'form',
    #         'target'    : 'new',
    #     }

    # @api.onchange('child_partner_ids')
    # def onchange_child_partner_ids(self):
    #     if self.child_partner_ids:
    #         self.env['res.partner'].browse(self.env.context.get('active_ids',False)).child_ids = self.child_partner_ids
    #
    # @api.multi
    # def write(self,vals):
    #     res = super(res_partner, self).write(vals)
    #     return res
