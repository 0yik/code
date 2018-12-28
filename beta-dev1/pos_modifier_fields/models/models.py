# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_config(models.Model):
    _inherit = 'pos.config'

    order_station = fields.Boolean(default=False)
    table_management = fields.Boolean(default=True)
    floor_ids2 = fields.Many2many('restaurant.floor', 'pos_config_restaurant_floor_rel_2', 'pos_config_id', 'floor_id', string="Floors")

    @api.model
    def create(self,vals):
        if vals.get('table_management') is False  and vals.get('floor_ids'):
            vals['floor_ids2'] =  vals.get('floor_ids')
            del vals['floor_ids']
        return super(pos_config,self).create(vals)

    @api.multi
    def write(self,vals):
        # import pdb
        # pdb.set_trace()
        chk_tbl_mgnt = 'table_management' in vals
        chk_flr = 'floor_ids' in vals

        if (chk_tbl_mgnt and not vals['table_management']) or (not self.table_management):
            if chk_flr:
                vals['floor_ids2'] = vals['floor_ids']
                del vals['floor_ids']
            else:
                vals['floor_ids'] = [(3, fid, 0) for fid in self.floor_ids.ids]
                vals['floor_ids2'] = [(6, 0, self.floor_ids.ids)]
                # vals['floor_ids'] = [(6, 0, [])]

        if (chk_tbl_mgnt and  vals['table_management']):
            if chk_flr:
                vals['floor_ids'] = vals['floor_ids'].extend(vals['floor_ids2'])
                vals['floor_ids2'] = [(6, 0, [])]
            else:
                vals['floor_ids2'] = [(3, fid, 0) for fid in self.floor_ids2.ids]
                vals['floor_ids'] = [(6, 0, self.floor_ids2.ids)]
                # vals['floor_ids2'] = [(6, 0, [])]        
        return super(pos_config,self).write(vals)