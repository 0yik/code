# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math, time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    
    from_date = fields.Date("From Date", default=lambda *a: (datetime.today() + relativedelta(days=-30)).strftime('%Y-%m-%d'))
    to_date = fields.Date("To Date", default=lambda *a: time.strftime('%Y-%m-%d'))
    remarks = fields.Html("Remarks")
    
    @api.multi
    def get_sale_order_line(self):
        sale_order_line = self.env['sale.order.line']
        order_line_ids = sale_order_line.search([('shipment_delivery_date', '>=', self.from_date), ('shipment_delivery_date', '<=', self.to_date)])
        return order_line_ids 
    
    @api.multi
    def get_total(self):
        sale_order_line = self.env['sale.order.line']
        order_line_ids = sale_order_line.search([('shipment_delivery_date', '>=', self.from_date), ('shipment_delivery_date', '<=', self.to_date)])
        quantity = 0.0
        amount = 0.0
        currency_id = False
        if order_line_ids:
            currency_id = order_line_ids[0].order_id.company_id.currency_id or False
            for x in order_line_ids:
                quantity += x.product_uom_qty
                amount += x.price_subtotal
        return {'qunatity': quantity, 'amount': amount, 'currency_id':currency_id, 'remarks': self.remarks}
    
    @api.multi
    def print_report(self):
        data = {}
        return self.env['report'].get_action(self, 'modifier_teo_sale_order_report.sale_order_report')