import json
from odoo import models, api, _, fields
from datetime import datetime, timedelta, date
import time

order_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
order_months_name = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul', '08':'Aug', '09':'Sep', '10':'Oct','11':'Nov','12':'Dec'}

class SalesBarChart(models.Model):
    _name = 'sales.bar.chart'
    
    name = fields.Char('Name')
    kanban_dashboard_graph_total = fields.Text(compute='_kanban_dashboard_graph')
    kanban_dashboard_graph_ferry = fields.Text(compute='_kanban_dashboard_graph_ferry')
    kanban_dashboard_graph_flf = fields.Text(compute='_kanban_dashboard_graph_flf')
    kanban_dashboard_graph_tug_and_burg = fields.Text(compute='_kanban_dashboard_graph_tug_and_burg')
    kanban_dashboard_graph_stevedoring = fields.Text(compute='_kanban_dashboard_graph_stevedoring')
    kanban_dashboard_graph_others = fields.Text(compute='_kanban_dashboard_graph_others')
        
    #Total
    @api.one
    def _kanban_dashboard_graph(self):
        if self.get_sale_bar_chart_datas():
            self.kanban_dashboard_graph_total = json.dumps(self.get_sale_bar_chart_datas())
        
    @api.multi
    def get_sale_bar_chart_datas(self):
        data = []
        to_invoice_records = self.env['sale.order'].search([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status','=','to invoice')])
        if to_invoice_records:
            for order_month in order_months: 
                month_total = 0.0
                month_name = order_months_name[order_month]
                for record in to_invoice_records:
                    if record.date_order.split('-')[1] == order_month:
                        month_total += record.amount_total
                data.append({'label':month_name, 'value':month_total, 'type': 'past'})
        return [{"values": data,}]
        
    #Ferry
    @api.one
    def _kanban_dashboard_graph_ferry(self):
        if self.get_sale_bar_chart_datas_ferry():
            self.kanban_dashboard_graph_ferry = json.dumps(self.get_sale_bar_chart_datas_ferry())
        
    @api.multi
    def get_sale_bar_chart_datas_ferry(self):
        data = []
        to_invoice_ferry_records = self.env['sale.order'].search([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status','=','to invoice'), ('requisition_id.business_unit.name', '=', 'Ferry')])
        if to_invoice_ferry_records:
            for order_month in order_months: 
                month_total = 0.0
                month_name = order_months_name[order_month]
                for ferry_record in to_invoice_ferry_records:
                    if ferry_record.date_order.split('-')[1] == order_month:
                        month_total += ferry_record.amount_total
                data.append({'label':month_name, 'value':month_total, 'type': 'past'})
        return [{"values": data}]
    
    #FLF
    @api.one
    def _kanban_dashboard_graph_flf(self):
        if self.get_sale_bar_chart_datas_flf():
            self.kanban_dashboard_graph_flf = json.dumps(self.get_sale_bar_chart_datas_flf())
        
    @api.multi
    def get_sale_bar_chart_datas_flf(self):
        data = []
        to_invoice_flf_records = self.env['sale.order'].search([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status','=','to invoice'), ('requisition_id.business_unit.name', '=', 'FLF')])
        if to_invoice_flf_records:
            for order_month in order_months: 
                month_total = 0.0
                month_name = order_months_name[order_month]
                for flf_record in to_invoice_flf_records:
                    if flf_record.date_order.split('-')[1] == order_month:
                        month_total += flf_record.amount_total
                data.append({'label':month_name, 'value':month_total, 'type': 'past'})
        return [{"values": data}]
        
    #Tug and Barge
    @api.one
    def _kanban_dashboard_graph_tug_and_burg(self):
        if self.get_sale_bar_chart_datas_tug_and_burg():
            self.kanban_dashboard_graph_tug_and_burg = json.dumps(self.get_sale_bar_chart_datas_tug_and_burg())
        
    @api.multi
    def get_sale_bar_chart_datas_tug_and_burg(self):
        data = []
        to_invoice_tug_and_burg_records = self.env['sale.order'].search([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status','=','to invoice'), ('requisition_id.business_unit.name', '=', 'Tug and Barge')])
        if to_invoice_tug_and_burg_records:
            for order_month in order_months: 
                month_total = 0.0
                month_name = order_months_name[order_month]
                for tug_burg_record in to_invoice_tug_and_burg_records:
                    if tug_burg_record.date_order.split('-')[1] == order_month:
                        month_total += tug_burg_record.amount_total
                data.append({'label':month_name, 'value':month_total, 'type': 'past'})
        return [{"values": data}]
                        
    #Stevedoring
    @api.one
    def _kanban_dashboard_graph_stevedoring(self):
        if self.get_sale_bar_chart_datas_stevedoring():
            self.kanban_dashboard_graph_stevedoring = json.dumps(self.get_sale_bar_chart_datas_stevedoring())
        
    @api.multi
    def get_sale_bar_chart_datas_stevedoring(self):
        data = []
        to_invoice_stevedoring_records = self.env['sale.order'].search([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status','=','to invoice'), ('requisition_id.business_unit.name', '=', 'Stevedoring')])
        if to_invoice_stevedoring_records:
            for order_month in order_months: 
                month_total = 0.0
                month_name = order_months_name[order_month]
                for stevedoring_record in to_invoice_stevedoring_records:
                    if stevedoring_record.date_order.split('-')[1] == order_month:
                        month_total += stevedoring_record.amount_total
                data.append({'label':month_name, 'value':month_total, 'type': 'past'})
        return [{"values": data}]
        
    #Others
    @api.one
    def _kanban_dashboard_graph_others(self):
        if self.get_sale_bar_chart_datas_others():
            self.kanban_dashboard_graph_others = json.dumps(self.get_sale_bar_chart_datas_others())
        
    @api.multi
    def get_sale_bar_chart_datas_others(self):
        data = []
        to_invoice_stevedoring_others = self.env['sale.order'].search([('state', 'not in', ('draft', 'sent', 'cancel')), ('invoice_status','=','to invoice'), ('requisition_id.business_unit.name', '=', 'Others')])
        if to_invoice_stevedoring_others:
            for order_month in order_months: 
                month_total = 0.0
                month_name = order_months_name[order_month]
                for others_record in to_invoice_stevedoring_others:
                    if others_record.date_order.split('-')[1] == order_month:
                        month_total += others_record.amount_total
                data.append({'label':month_name, 'value':month_total, 'type': 'past'})
        return [{"values": data}]                        
