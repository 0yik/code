from odoo import api, fields, models

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def action_set_won2(self):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 100})
        return True

    @api.multi
    def action_set_won(self):
        return {
            'name': 'Customer Wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'customer.wizard',
            'target': 'new',
            'context': {
                'lead_id': self.id,
                'default_partner_name': self.partner_name,
                'default_street': self.street,
                'default_street2': self.street2,
                'default_city': self.city,
                'default_state_id': self.state_id.id,
                'default_zip': self.zip,
                'default_country_id': self.country_id.id,
                'default_contact_name': self.contact_name,
                'default_title': self.title.id,
                'default_function': self.function,
                'default_phone': self.phone,
                'default_mobile': self.mobile,
                'default_fax': self.fax,
                'default_email': self.email_from
            },
        }

Lead()