# -*- coding: utf-8 -*-
from odoo import models, fields, api

class res_branch(models.Model):
    _inherit = 'res.branch'

    company_id = fields.Many2one('res.company', string='Company', required=False)
    is_warehouse = fields.Boolean('Is A Warehouse')
    country_code = fields.Char(string="Counter code", size=12)
    warehouse_id = fields.Many2one('stock.warehouse','Warehouse')
    location_id  = fields.Many2one('stock.location','Location',related='warehouse_id.lot_stock_id')

    @api.model
    def create(self, vals):
        warehouse_vals = {}
        if vals.get('is_warehouse') and not self.env.context.get('from_location'):
            warehouse_vals['name'] = vals.get('name')
            warehouse_vals['code'] = vals.get('country_code','')
            warehouse_vals['is_shop'] = True
            warehouse_vals['company_id'] = vals.get('company_id',False)
            warehouse_id = self.env['stock.warehouse'].with_context({'from_branch': True}).create(warehouse_vals)
            vals.update({'warehouse_id':warehouse_id.id or False})
        return super(res_branch, self).create(vals)


    @api.multi
    def write(self,vals):
        if vals.get('is_warehouse',False):
            if not self.warehouse_id:
                warehouse_vals = {}
                location_id = self.env['stock.location'].search([('name','=',self.country_code or vals.get('country_code',False))])
                if location_id:
                    location_id.unlink()
                warehouse_vals['name'] = self.name or vals.get('name')
                warehouse_vals['code'] = self.country_code or vals.get('country_code', '')
                warehouse_vals['is_shop'] = True
                warehouse_vals['company_id'] = self.company_id.id or vals.get('company_id', False)
                warehouse_id = self.env['stock.warehouse'].with_context({'from_branch': True}).create(warehouse_vals)
                vals.update({'warehouse_id': warehouse_id.id or False})
        res= super(res_branch, self).write(vals)
        return res
res_branch()