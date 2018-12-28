from odoo import api, models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    temp_password = fields.Char('Password')
    
    @api.model
    def create(self, vals):
        if vals.get('password'):
            vals['temp_password'] = vals.get('password')
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('password'):
            vals['temp_password'] = vals.get('password')
        return super(ResUsers, self).write(vals)