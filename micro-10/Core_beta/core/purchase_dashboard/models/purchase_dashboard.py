# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo import tools
import locale
from time import gmtime, strftime

class HRDashboard(models.Model):
    _name = 'purchase.dashboard'
    _description = "HR Dashboard"

    name = fields.Char("Name")

    def get_local_dt(self, date_time):
        tz = "Singapore"
        cur_date = date_time
        local_tz = pytz.timezone(self.env.user.tz or tz)
        local_dt = cur_date.replace(tzinfo=pytz.utc
                                    ).astimezone(local_tz)
        return local_dt

    @api.model
    def get_purchase_dashboard_details(self):
        data = {}
        cr = self.env.cr
        today = self.get_local_dt(datetime.now())
        from_date_of_month = today.strftime("%Y-%m-1 0:00:00")
        end_date = today + relativedelta(months=+1)
        end_date_of_month = end_date.strftime("%Y-%m-1 0:00:00")

        start_of_a_day = today.strftime("%Y-%m-%d 0:00:00")
        end_of_a_day = today.strftime("%Y-%m-%d 23:59:59")

        month_date = datetime.strftime(today, "%B-%Y")
        date_of_today = today.strftime("%d/%m/%Y")
        currency = self.env.user.self.env.user.company_id.currency_id.symbol

        Purchase = self.sudo().env['purchase.order']
        PurchaseRequest = self.sudo().env['purchase.request']
        PurchaseRequisition = self.sudo().env['purchase.requisition']
        StockPicking = self.sudo().env['stock.picking']
        Vendor = self.sudo().env['res.partner']
        Invoice = self.sudo().env['account.invoice']
        ReorderingRule = self.sudo().env['stock.warehouse.orderpoint']

        domain_purchase_in_a_month = [('date_order','>=',from_date_of_month),('date_order','<=',end_date_of_month)]
        domain_stock_picking_in_a_day = [('min_date','>=',start_of_a_day),('min_date','<=',end_of_a_day)]


        #a. Purchase Request Today
        purchase_purchase_request_today = PurchaseRequest.search(
            [])
        number_of_purchase_request_today = len(purchase_purchase_request_today)

        #b. Total Request for Quotation in a month
        rfq = Purchase.search([('state','in',('draft','sent','bid','cancel', 'confirmed'))] + domain_purchase_in_a_month)
        number_of_rfq = len(rfq)
        total_amount_of_rfq = sum(rfq.mapped('amount_total'))

        #c. This Month Purchase
        purchase_month = Purchase.search(domain_purchase_in_a_month+[('state','not in',('draft','sent','bid', 'confirmed'))])
        number_of_purchase_month = len(purchase_month)
        total_amount_of_purchase_month = sum(purchase_month.mapped('amount_total'))


        #d. Total Purchase
        current_year = datetime.now().strftime("%Y")
        domain_in_current_year = [('date_order','<=',current_year+'-12-31'), ('date_order','>=',current_year+'-01-1')]
        purchase_total= Purchase.search(domain_in_current_year+[('state', 'not in', ('draft', 'sent', 'bid', 'confirmed'))])
        number_of_purchase_total = len(purchase_total)
        total_amount_of_purchase_total = sum(purchase_total.mapped('amount_total'))

        #e. Today's Incoming Shipment
        incoming_shipment = StockPicking.search(domain_stock_picking_in_a_day + [('state','in',('assigned','partially_available'))])
        number_of_incoming_shipment = len(incoming_shipment)

        #f. Pending Shipments
        pending_shipment = StockPicking.search(['|','|',('state','in',('confirmed', 'waiting')),
                                                ('backorder_id', '!=', False),
                                                '&',('state','in', ('confirmed', 'waiting', 'assigned')),('min_date', '<', today.strftime('%Y-%m-%d %H:%M:%S'))])
        number_of_pending_shipment = len(pending_shipment)

        #g. Invoice
        invoices = Invoice.search([('type', 'in', ['in_invoice', 'in_refund']), ('state','=','open')])

        # Vendors
        cr.execute("Select partner_id, sum(amount_total) as total from purchase_order where state='purchase' group by partner_id order by total desc limit 10")
        results = cr.fetchall()
        top_ten_vendor = []
        top_ten_amount = []
        count = 0
        for res in results:
            if count == 10:
                break
            top_ten_vendor.append(self.sudo().env['res.partner'].browse(res[0]).name)
            top_ten_amount.append(res[1])
            count+=1

        #i. Total PR To Approve/In Progress:
        purchase_request_to_approve = PurchaseRequest.search([('state','=','to_approve')])
        number_purchase_request_to_approve = len(purchase_request_to_approve)

        #j. Total Tender:
        purchase_tender = PurchaseRequisition.search([
            ('type_id.name', '=', 'Purchase Tender'),
            ('state', '=', 'in_progress'),
            '|',('date_end', '<', today.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
            ('date_end', '=', False),
                                                      ])
        number_of_purchase_tender = len(purchase_tender)

        #k. Low Stock Products:
        low_stock_products = []
        reordering_rule_ids = ReorderingRule.search([])
        for rule in reordering_rule_ids:
            if rule.product_id.qty_available <= rule.product_min_qty:
                low_stock_products.append(rule.product_id.id)

        number_of_low_stock_products = len(low_stock_products)

        data.update({
            'month_date': month_date,
            'current_year': current_year,
            'date_of_today': date_of_today,
            'number_of_rfq': number_of_rfq,
            'rfq' : rfq.ids,
            'total_amount_of_rfq': tools.ustr(locale.format("%.2f", float(math.ceil(total_amount_of_rfq*100)/100), grouping=True)),
            'number_of_purchase_month': number_of_purchase_month,
            'total_amount_of_purchase_month': tools.ustr(locale.format("%.2f", float(math.ceil(total_amount_of_purchase_month*100)/100), grouping=True)),
            'purchase_month' : purchase_month.ids or [],
            'number_of_purchase_total': number_of_purchase_total,
            'purchase_total': purchase_total.ids or [],
            'total_amount_of_purchase_total': tools.ustr(locale.format("%.2f", float(math.ceil(total_amount_of_purchase_total*100)/100), grouping=True)),
            'number_of_purchase_request_today': number_of_purchase_request_today,
            'purchase_purchase_request_today': purchase_purchase_request_today.ids or [],
            # 'vendors': vendors.ids or [],
            # 'number_of_vendors': len(vendors),
            'top_ten_vendor' : top_ten_vendor,
            'top_ten_amount' : top_ten_amount,
            'invoices': invoices.ids,
            'number_of_invoices': len(invoices),
            'incoming_shipment' : incoming_shipment.ids,
            'number_of_incoming_shipment' : number_of_incoming_shipment,
            'pending_shipment' : pending_shipment.ids,
            'number_of_pending_shipment' : number_of_pending_shipment,
            'purchase_request_to_approve' : purchase_request_to_approve.ids,
            'number_purchase_request_to_approve' : number_purchase_request_to_approve,
            'number_of_low_stock_products' : number_of_low_stock_products,
            'low_stock_products' : low_stock_products,
            'purchase_tender' : purchase_tender.ids,
            'number_of_purchase_tender' : number_of_purchase_tender,
            'currency' : currency,
        })
        return data


