import json
from odoo import models, api, _, fields
from datetime import datetime, timedelta, date
import time

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    kanban_dashboard = fields.Text(compute='_kanban_dashboard')
	
    @api.one
    def _kanban_dashboard(self):
        if self.get_journal_dashboard_datas():
            self.kanban_dashboard = json.dumps(self.get_journal_dashboard_datas())
        
    @api.multi
    def get_journal_dashboard_datas(self):
        currency = self.env.user.company_id.currency_id
        #current date quotation
        current_quotations_count = 0
        current_quotations_total = 0
        current_quotations = self.env['sale.order'].search([('state','=','draft'),('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
        for current_quotation in current_quotations:
            current_quotations_count = current_quotations_count + 1
            current_quotations_total = current_quotations_total + current_quotation.amount_total
        
        #first day of month
        first_day = datetime.now().replace(day=1)
        
        #current month quotation
        month_quotations_count = 0
        month_quotations_total = 0
        month_quotations = self.env['sale.order'].search([('state','=','draft'),('date_order', '>=', first_day.strftime('%Y-%m-%d 00:00:00')),('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
        for month_quotation in month_quotations:
            month_quotations_count = month_quotations_count + 1
            month_quotations_total = month_quotations_total + month_quotation.amount_total
        
        #toady sale orders
        current_so_count = 0
        current_so_total = 0
        current_sale_orders = self.env['sale.order'].search([('state','=','sale'),('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
        for current_sale_order in current_sale_orders:
            current_so_count = current_so_count + 1
            current_so_total = current_so_total + current_sale_order.amount_total
            
        #current month sale orders
        month_so_count = 0
        month_so_total = 0
        month_sale_orders = self.env['sale.order'].search([('state','=','sale'),('date_order', '>=', first_day.strftime('%Y-%m-%d 00:00:00')),('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
        for month_sale_order in month_sale_orders:
            month_so_count = month_so_count + 1
            month_so_total = month_so_total + month_sale_order.amount_total
            
        #Sales to Invoice
        to_invoice_count = 0
        to_invoice_total = 0
        to_invoice_sale_orders = self.env['sale.order'].search([('invoice_status','=','to invoice'), ('date_order', '<=', datetime.now().strftime('%Y-%m-%d 23:23:59'))])
        for to_invoice_sale_order in to_invoice_sale_orders:
            to_invoice_count = to_invoice_count + 1
            to_invoice_total = to_invoice_total + to_invoice_sale_order.amount_total

        return {
            'currency_symbol': currency.symbol,
            'total_today_quotations': float("{0:.2f}".format(current_quotations_total)),
            'count_today_quotations': current_quotations_count,
            'total_today_so': float("{0:.2f}".format(current_so_total)),
            'count_today_so': current_so_count,
            'total_month_quotations': float("{0:.2f}".format(month_quotations_total)),
            'count_month_quotations': month_quotations_count,
            'total_month_so': float("{0:.2f}".format(month_so_total)),
            'count_month_so': month_so_count,
            'total_to_invoice': float("{0:.2f}".format(to_invoice_total)),
            'count_to_invoice': to_invoice_count,
            } 
