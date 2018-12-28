from odoo import api, fields, models, _


class MasterReason(models.Model):
    _name = 'master.reason'

    name = fields.Char(string='Reason', required=True)
    description = fields.Char('Reason Description')
