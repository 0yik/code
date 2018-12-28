from odoo import api, fields, models, _

class AccessRightsGroup(models.Model):
    _name = 'access.rights.group'
    _inherit = ['mail.thread']
    _description = 'Access Rights Group'
    _order = 'id desc'

    name = fields.Char(track_visibility='onchange', string='Group Name')
    group_ids = fields.Many2many('res.groups', track_visibility='onchange', string='Groups')

AccessRightsGroup()