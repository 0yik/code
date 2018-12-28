# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    
    def _get_account_manager(self):
        group_id = self.env.ref('hilti_modifier_accessrights.group_hilti_account_manager')
        if group_id and group_id.users:
            return [('id', 'in', group_id.users.ids)]
        else:
            return [('id', 'in', [])]
        
    
    account_number = fields.Char(string="Account Number")
    job_title = fields.Char(string="Job Title")
    is_vip = fields.Boolean(string="VIP")
    project_ids = fields.Many2many('project.project','rel_partner_project','partner_id' ,'project_id', string="Project")
    booking_ids = fields.One2many('project.booking', 'partner_id', string="Booking")
    account_manager_id = fields.Many2one('res.users', string="Account Manager", domain=_get_account_manager)
    
    
    @api.onchange('parent_id')
    def _onchange_parent(self):
        if self.parent_id:
            self.account_number = self.parent_id.account_number
    
    
class res_users(models.Model):
    _inherit = 'res.users'
    
    equipment_ids = fields.Many2many('product.product', string="Equipment")
    sic_access = fields.Many2many('product.product', string="SIC Access")
    phone_number = fields.Char(string="Phone Number")
    address = fields.Char(string="Address")
