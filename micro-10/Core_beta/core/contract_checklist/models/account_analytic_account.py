from odoo import fields,models,api,_

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    checklist_ids = fields.One2many('contract.checklist','account_alnalytic_id',string='Checklist')


class contract_checklist(models.Model):
    _name = 'contract.checklist'
    _rec_name = 'name'

    account_alnalytic_id = fields.Many2one('account.analytic.account')
    name = fields.Text('Description')
    pic_id = fields.Many2one('res.users','PIC')
    done = fields.Boolean('Done')


