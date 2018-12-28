from odoo import api, fields, models, _


class account_chart(models.TransientModel):
    _name = "account.chart"
    _description = "Account chart"

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    target_move =  fields.Selection([('posted', 'All Posted Entries'), ('all', 'All Entries')], 'Target Moves', required=True)

    @api.multi
    def account_chart_open_window(self):
        result_context = {}
        action = self.env.ref('chart_of_tax.action_chart_of_tax_tree').read()[0]
        result_context.update({'target_move': self.target_move})
        if self.date_from:
            result_context.update({'date_from': self.date_from})
        if self.date_to:
            result_context.update({'date_to': self.date_to, })
        if result_context:
            action['context'] = str(result_context)
        return action
