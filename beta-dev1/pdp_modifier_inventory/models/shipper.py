from odoo import models, fields, api

class shipper(models.Model):
    _name = 'shipper'

    code            = fields.Char('Code',size=12)
    name            = fields.Char('Name')
    address         = fields.Text('Address')
    zip_code        = fields.Char('Zip Code')
    state_id        = fields.Many2one('res.country.state','State')
    phone           = fields.Char('Phone')
    city            = fields.Many2one('employee.city','City')
    fax             = fields.Char('Fax')
    country_id      = fields.Many2one('res.country','Country')
    contact         = fields.Char('Contact')
    active          = fields.Boolean('Active',default=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
                result.append((record.id, record.code and record.code or ''+ ',' + record.name and record.name or ''))
        return result