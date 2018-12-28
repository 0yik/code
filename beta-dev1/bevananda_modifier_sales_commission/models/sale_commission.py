# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    #378401
##############################################################################
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime


class TargetGroup(models.Model):
    _inherit = 'target.group'

    job_id = fields.Many2one('hr.job','Job Role', required=True)
    distributor = fields.Boolean('Is a Distributor')
    date_start = fields.Date('Date Start', required=True)
    date_end = fields.Date('Date End', required=True)
    reference = fields.Char('Reference')
    status = fields.Selection([
        ('distributor', 'Distributor'),
        ('sales_person', 'Sales Person'),
    ], string='Status',default='sales_person')
    sale_category = fields.Selection([
        ('basic', 'Basic'),
        ('advance', 'Advance'),
    ], string='Sales Category', default='basic', required=True)
    target_lines = fields.One2many('target.lines', 'target_group_id', 'Target lines')
    
    @api.onchange('distributor')
    def onchnage_distributor(self):
        if self.distributor == True:
            self.status = 'distributor'
        else:
            self.status = 'sales_person'
    
class TargetLine(models.Model):
    _inherit = 'target.lines'

    target_group_id = fields.Many2one('target.group')#O2M
    product_tmpl_id = fields.Many2one('product.template','Product')
    product_type = fields.Char('Product Type', readonly=True, store=True)
    points = fields.Float('Points')
    amount = fields.Float('Commission')
    is_distributor = fields.Boolean(related='target_group_id.distributor',string='Is a Distributor')
    #is_distributor = fields.Boolean('Is a Distributor')
    
    @api.onchange('product_tmpl_id')
    def onchnage_product_tmpl_id(self):
        if self.product_tmpl_id.type:
            if self.product_tmpl_id.type == 'product':
                pro_type = 'Stockable Product'
            elif self.product_tmpl_id.type == 'consu':
                pro_type = 'Consumable'
            else:
                pro_type = 'Service'
            self.product_type = pro_type        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
