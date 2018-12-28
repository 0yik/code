# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _
import time


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_default_warehouse(self):
        company_id = self.env.user._get_company()
        print company_id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company_id)],limit=1)
        return warehouse_ids[0] or False
    
    default_warehouse_id = fields.Many2one('stock.warehouse','Default Warehouse', default=_get_default_warehouse)
    active_warehouse_id = fields.Many2one('stock.warehouse','Active Warehouse')
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
