from odoo import fields, models


class City(models.Model):
    _name = 'city.city'
    
    name = fields.Char('Name')
    state_id = fields.Many2one('res.country.state','State')
    country_id = fields.Many2one('res.country', related='state_id.country_id', string='Country')
    
class Branch(models.Model):
    _inherit = 'res.branch'
    
    city_id = fields.Many2one('city.city','City')
