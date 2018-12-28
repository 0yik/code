from odoo import api, fields, models,_


class Lead2OpportunityPartner(models.TransientModel):

    _inherit = 'crm.lead2opportunity.partner'

    @api.multi
    def action_apply(self):
        """ Convert lead to opportunity or merge lead and opportunity and open
            the freshly created opportunity view.
        """
        self.ensure_one()
        values = {
            'team_id': self.team_id.id,
        }

        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        if self.name == 'merge':
            leads = self.opportunity_ids.merge_opportunity()
            if leads.type == "lead":
                values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
                self.with_context(active_ids=leads.ids)._convert_opportunity(values)
            elif not self._context.get('no_force_assignation') or not leads.user_id:
                values['user_id'] = self.user_id.id
                leads.write(values)
        else:
            leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
            values.update({'lead_ids': leads.ids, 'user_ids': [self.user_id.id]})
            self._convert_opportunity(values)
            for lead in leads:
                if lead.partner_id and lead.partner_id.user_id != lead.user_id:
                    self.env['res.partner'].browse(lead.partner_id.id).write({'user_id': lead.user_id.id})

        contract_obj = self.env['account.analytic.account']
        vals = {}
        vals.update({
            'name':leads.name,
            'type':'contract',
            'is_project': True
        })
        contract_id = contract_obj.create(vals)
        leads.contract_id = contract_id.id

        return leads[0].redirect_opportunity_view()

class Lead(models.Model):

    _inherit = "crm.lead"

    contract_id = fields.Many2one('account.analytic.account','Contract')

    # @api.multi
    # def redirect_opportunity_view(self):
    #     self.ensure_one()
    #     # Get opportunity views
    #     form_view = self.env.ref('analytic.view_account_analytic_account_form')
    #     tree_view = self.env.ref('analytic.view_account_analytic_account_list')
    #     return {
    #         'name': _('Contracts'),
    #         'view_type': 'form',
    #         'view_mode': 'tree, form',
    #         'res_model': 'account.analytic.account',
    #         'res_id': self.contract_id.id,
    #         'view_id': False,
    #         'views': [
    #             (form_view.id, 'form'),
    #             (tree_view.id, 'tree'),
    #             (False, 'kanban'),
    #             (False, 'calendar'),
    #             (False, 'graph')
    #         ],
    #         'type': 'ir.actions.act_window',
    #         'context': {}
    #     }



