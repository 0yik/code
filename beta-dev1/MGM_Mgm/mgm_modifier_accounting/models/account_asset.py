from odoo import api, fields, models, _

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    responsible_id = fields.Many2one('hr.employee', 'Responsible')