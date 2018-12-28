from odoo import api, fields, models

class AccountAssetLocation(models.Model):
    _name = 'account.asset.location'

    name = fields.Char('Location')

AccountAssetLocation()