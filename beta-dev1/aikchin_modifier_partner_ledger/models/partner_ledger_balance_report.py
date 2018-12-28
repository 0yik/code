from odoo import models, fields, api

class aikchin_modifier_partner_ledger(models.TransientModel):
    _inherit = 'account.aged.trial.balance'

    partner2_ids = fields.One2many('partner.ledger.line.partners','partner_ledger_balance_id',string='Partners')

    @api.onchange('partner2_ids')
    def onchange_partner2_ids(self):
        if self.partner2_ids:
            for partner in self.partner2_ids:
                self.partner_ids += partner.name

    def _print_report(self,data):
        self.partner2_ids = None
        res = super(aikchin_modifier_partner_ledger, self)._print_report(data)
        return res