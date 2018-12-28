# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    pos_ids = fields.Many2many('pos.config', string="Point of Sale")
    is_brand_visible = fields.Boolean(string="Brand Visible")
    # brand_ids = fields.Many2many("product.brand", 'user_brand_rel', 'user_id', 'brand_id', string="Brand")
    brand_id = fields.Many2one('product.brand', string="Brand")
    screen_type = fields.Selection([
            ('waiter', 'Waiter'),
            ('kitchen', 'Kitchen'), ], string='Session Type', default='waiter')
    brand_branch_ids = fields.Many2many('res.branch', string="Branch", compute='_get_branch_ids', store=True)

    @api.onchange('branch_id')
    def onchange_brand_id(self):
        '''Method to compute brand'''
        self.brand_id = self.branch_id.brand_id.id if self.branch_id.brand_id else False

    @api.multi
    @api.depends('brand_id')
    def _get_branch_ids(self):
        '''Method to compute branches'''
        for rec in self:
            rec.brand_branch_ids = [branch_obj.branch_id.id for branch_obj in rec.brand_id.branch_ids]
        return True

    @api.multi
    def set_pos_group(self,values):
        values['is_brand_visible'] = False
        if 'sel_groups_80' in values.keys():
            values['is_brand_visible'] = True
        if 'sel_groups_80' in values.keys() and values['sel_groups_80'] == False:
            values['is_brand_visible'] = False
        if ('sel_groups_80' in values.keys() and values['sel_groups_80']) or ('sel_groups_74_75' in values.keys() and values['sel_groups_74_75'] == self.env.ref('branch.group_branch_user_manager').id):
            values['sel_groups_36_37'] = self.env.ref('point_of_sale.group_pos_manager').id
        return values

    @api.model
    def create(self, values):
        values = self.set_pos_group(values)
        return super(ResUsers, self).create(values)

    @api.multi
    def write(self, values):
        values = self.set_pos_group(values)
        return super(ResUsers, self).write(values)

ResUsers()
