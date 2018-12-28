from odoo import api, fields, models, _


class CoaWizard(models.TransientModel):
    _name = "coa.wizard"
    _description = "Chart Of Accounts"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'), ('all', 'All Entries')], 'Target Moves', default='posted')

    @api.multi
    def chart_of_account_open_window(self):
        result_context = {}
        action = self.env.ref('clickable_chartofaccount.action_chart_of_accounts_tree').read()[0]
        result_context.update({'target_move': self.target_move})
        if self.date_from:
            result_context.update({'date_from': self.date_from})
        if self.date_to:
            result_context.update({'date_to': self.date_to, })
        if result_context:
            action['context'] = str(result_context)
        return action

CoaWizard()
