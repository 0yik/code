from odoo import fields, models, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    today_date      =   fields.Date('Date Today',default=fields.Date.today)

class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    swift_code      =   fields.Char('Swift Code')
    street          =   fields.Char('Street')
    street2         =   fields.Char('Street')
    city            =   fields.Char('City')
    state_id        =   fields.Many2one('res.country.state')
    zip             =   fields.Char('Zip')
    country_id      =   fields.Many2one('res.country')