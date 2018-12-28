from odoo import models, fields, api

class driver(models.Model):
    _name = 'driver'

    code        = fields.Char('Code',size=12)
    name        = fields.Char('Name')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.code and record.code or ''+ ',' + record.name and record.name or ''))
        return result