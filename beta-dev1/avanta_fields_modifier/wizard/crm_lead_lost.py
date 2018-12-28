# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    lead_id = fields.Many2one('crm.lead', 'Lost Reason')

    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        if leads:
            leads.write({'lost_reason': self.lost_reason_id.id})
        else:
            self.lead_id.write({'lost_reason': self.lost_reason_id.id})
        return leads.action_set_lost()

CrmLeadLost()
