from odoo import api, fields, models

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def _compute_contract_id(self):
        for record in self:
            contract_id = self.env['account.analytic.account'].sudo().search([('crm_lead_id','=',record.id)], limit=1)
            record.contract_id = contract_id and contract_id.id

    contract_id = fields.Many2one('account.analytic.account', compute='_compute_contract_id', string='Contract')

    @api.model
    def create(self, vals):
        lead_id = super(Lead, self).create(vals)
        self.env['account.analytic.account'].sudo().create({
            'type': 'contract',
            'is_project': True,
            'name': lead_id.name,
            'crm_lead_id': lead_id.id,
            'partner_id': lead_id.partner_id.id
        })
        self.env['project.project'].sudo().create({
            'name': lead_id.name,
            'type': 'contract',
            'crm_lead_id': lead_id.id,
            'partner_id': lead_id.partner_id.id
        })
        return lead_id

    @api.multi
    def action_view_contract(self):
        action = self.env.ref('stable_account_analytic_analysis.action_account_analytic_overdue_all').read()[0]
        action['domain'] = [('crm_lead_id','in',self.ids)]
        return action

Lead()

class Contract(models.Model):
    _inherit = 'account.analytic.account'

    crm_lead_id = fields.Many2one('crm.lead', 'CRM Lead')

Contract()

class Project(models.Model):
    _inherit = 'project.project'

    crm_lead_id = fields.Many2one('crm.lead', 'CRM Lead')

Project()