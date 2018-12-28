from odoo import api, models

class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    @api.multi
    def action_apply(self):
        return super(Lead2OpportunityPartner, self).action_apply()

Lead2OpportunityPartner()