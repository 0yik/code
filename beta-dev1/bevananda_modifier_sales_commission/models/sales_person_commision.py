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
from datetime import datetime


class SalesPersonCommision(models.Model):
    _name = 'sales.person.commision'
    _rec_name = 'sales_person_id'
    
    #name = fields.Char('Sales Person')
    sales_person_id = fields.Many2one('res.users', 'Sales Person')
    quater_id = fields.Many2one('commission.quarter','Quater', required=True)
    sales_taem_id = fields.Many2one('crm.team','Sales Team', required=True)
    Period_from = fields.Date('Period From', required=True)
    Period_to = fields.Date('Period To', required=True)
    sales_person_commision_lines = fields.One2many('sales.person.commision.order.line', 'sales_person_commision_id', string='Sale Order Detail')
    actual_margin_total = fields.Monetary(string='Total Actual Margin', store=True, readonly=True, compute='_amount_all')
    commission_total = fields.Monetary(string='Total Commision', store=True, readonly=True, compute='_amount_all')
    turnover_total = fields.Monetary(string='Turnover Total', store=True, readonly=True, compute='_amount_all')
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True, default=lambda self: self.env.user.company_id.currency_id)
    
    
        
class SalesPersonCommisionOrderLine(models.Model):
    _name = "sales.person.commision.order.line"
    
    sales_person_commision_id = fields.Many2one('sales.person.commision', string='Sales Person Commision Id', required=True)#O2M
    name = fields.Char('SO No.')
    so_date = fields.Datetime('SO Date', required=True)
    product_id = fields.Many2one('product.product', string='Product Name', required=True)
    sub_total = fields.Float('Sub Total')
    ending_total = fields.Float('Ending Total')
    commission = fields.Float('Commision')
    actual_margin = fields.Float('Actual Margin')
    point = fields.Float('Point Gain')
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
