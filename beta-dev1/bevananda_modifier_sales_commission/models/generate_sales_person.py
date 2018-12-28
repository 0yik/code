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
from datetime import datetime, timedelta, date
import time
from dateutil.relativedelta import relativedelta
from ast import literal_eval


class GenerateSalesPerson(models.Model):
    _name = 'generate.sales.person'

    name = fields.Char('Batch Name')
    quater_id = fields.Many2one('commission.quarter','Quater', required=True)
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    sales_taem_id = fields.Many2one('crm.team','Sales Team', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated','Sales Person Generated'),
        ('done', 'Done'),
    ], string="State", default='draft', readonly=True)#compute='_change_states',
    sales_person_lines = fields.One2many('res.users', 'gen_sale_person_id', string='Analytic lines')
    
   
    @api.multi
    def btn_generate(self):
        sales_team_record = self.env['crm.team'].browse(self.sales_taem_id.id)
        if sales_team_record.member_ids:
            self.sales_person_lines = sales_team_record.member_ids     
            #Add Code Here
            for sales_person_line in self.sales_person_lines:
                sales_person_commision_lines = []
                product_list = []
                #is datefrom-dateto
                #from_date = datetime.strptime(self.date_from, '%Y-%m-%d')
                #to_date = datetime.strptime(self.date_to, '%Y-%m-%d')
                #records = self.env['sale.order'].search([('date_order', '>=', to_date.strftime('%Y-%m-%d 00:00:00')),('date_order', '<=', from_date.strftime('%Y-%m-%d 23:23:59')),('user_id','=',sales_person_line.id)])
                #print"records====>>>>",records
                sale_order_line_records = self.env['sale.order'].search([('user_id','=',sales_person_line.id)]).mapped('order_line')
                
                #Sale Order Line
                ending_total_dict = {}
                turnover_total = 0.0
                actual_margin_total = 0.0
                final_commission_total = 0.0
                ending_total_amount = 0.0
                points = 0.0
                if sale_order_line_records:
                    for sale_order_line_record in sale_order_line_records:
                        #Commision Related
                        target_lines = self.env['target.group'].search([('status','=','sales_person')]).mapped('target_lines')
                        commission_total_dict = {}
                        total_commission = 0.0
                        for target_line in target_lines:
                            if target_line.product_tmpl_id == sale_order_line_record.product_id.product_tmpl_id:
                                if target_line.product_tmpl_id in commission_total_dict:
                                    commission_total = commission_total_dict[target_line.product_tmpl_id] + target_line.amount
                                    commission_total_dict[target_line.product_tmpl_id] = commission_total
                                else:
                                    commission_total_dict[target_line.product_tmpl_id] = target_line.amount        
                        uniq_product_commission_total = {}
                        if commission_total_dict:
                            total_commission = commission_total_dict[sale_order_line_record.product_id.product_tmpl_id]
                            if commission_total_dict[sale_order_line_record.product_id.product_tmpl_id] not in product_list:
                                final_commission_total += commission_total_dict[sale_order_line_record.product_id.product_tmpl_id]
                                product_list.append(commission_total_dict[sale_order_line_record.product_id.product_tmpl_id])
                        #Ending total
                        if sale_order_line_record.product_id in ending_total_dict:
                            ending_total = ending_total_dict[sale_order_line_record.product_id] + sale_order_line_record.price_subtotal
                            ending_total_dict[sale_order_line_record.product_id] = ending_total
                        else:    
                            ending_total_dict[sale_order_line_record.product_id] = sale_order_line_record.price_subtotal
                        ending_total_amount = ending_total_dict[sale_order_line_record.product_id]
                        
                        #count total Turnover and total Actual_Margin
                        turnover_total += sale_order_line_record.price_subtotal
                        actual_margin_total += sale_order_line_record.order_id.margin
                        sales_person_commision_lines.append((0, 0,
                                    {'name': sale_order_line_record.order_id.name,
                                     'so_date':sale_order_line_record.order_id.date_order,
                                     'product_id':sale_order_line_record.product_id.id,
                                     'sub_total':sale_order_line_record.price_subtotal,
                                     'ending_total':ending_total_amount or False ,
                                     'commission':total_commission or False,
                                     'actual_margin':sale_order_line_record.order_id.margin,
                                     #'point':False,
                                     }
                                ))         
                vals = {'sales_person_id': sales_person_line.id,
                        'quater_id':self.quater_id.id,
                        'sales_taem_id':self.sales_taem_id.id,
                        'Period_from':self.date_from,
                        'Period_to':self.date_to,
                        'actual_margin_total':actual_margin_total or False,
                        'commission_total':final_commission_total or False,
                        'turnover_total':turnover_total or False,
                        'sales_person_commision_lines':sales_person_commision_lines,
                        }
                
                self.env['sales.person.commision'].create(vals)
            self.state = 'generated'
            
    @api.multi
    def btn_set_done(self):
        self.state = 'done'
            
    @api.multi
    def open_commision_reward(self):
        action = self.env.ref('sale_commission_target_gt.action_target_group').read()[0] 
        return action
        
class ResUsers(models.Model):
    _inherit = 'res.users'
    
    gen_sale_person_id = fields.Many2one('generate.sales.person','Generate Sales Person Id') #O2M
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
