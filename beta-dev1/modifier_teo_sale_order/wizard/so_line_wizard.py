# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math, time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SOLineWizard(models.TransientModel):
    _name = 'so.line.wizard'
    
    @api.model
    def default_get(self, fields_list):
        res = super(SOLineWizard, self).default_get(fields_list)
        so_line_list = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        from_date = False
        to_date = False
        for line in so_line_list:
            if not from_date:
                from_date = line.shipment_delivery_date
            if line.shipment_delivery_date and line.shipment_delivery_date < from_date:
                from_date = line.shipment_delivery_date
            if line.shipment_delivery_date and line.shipment_delivery_date > to_date:
                to_date = line.shipment_delivery_date
        res.update({'from_date' : from_date,
                    'to_date': to_date})
        return res
    
    from_date = fields.Date("From Date", default=lambda *a: (datetime.today() + relativedelta(days=-30)).strftime('%Y-%m-%d'))
    to_date = fields.Date("To Date", default=lambda *a: time.strftime('%Y-%m-%d'))
    remarks = fields.Html("Remarks")
    
    @api.multi
    def generate_so(self):
        data = {}
        main_lst = []
        line_lst = []
        quantity = 0.0
        amount = 0.0
        currency_id = False
        so_line_list = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        for line in so_line_list:
            if line.shipment_delivery_date >= self.from_date and line.shipment_delivery_date <= self.to_date:
                line_dict = {'image': line.product_id.image_medium,
                             'ship_dely_date': line.shipment_delivery_date,
                             'so_id' : line.order_id.name,
                             'ship_buyer_order_no' : line.shipment_buyer_order_no,
                             'line': line.id,
                             'stk_id': line.product_id.name,
                             'description': line.name,
                             'final_destination': line.final_destination,
                             'latest_rev_date': line.original_delivery_date,
                             'price': line.price_unit,
                             'qty': line.product_uom_qty,
                             'total': line.price_subtotal,
                             'fiber_content': line.fiber_content,
                             'buyer_name': line.order_id.buyer_name,
                             }
                line_lst.append(line_dict)
                quantity += line.product_uom_qty
                amount += line.price_subtotal
                currency_id = line.order_id.company_id.currency_id.symbol or False
        main_lst.append({'lines' : line_lst,
                         'quantity': quantity,
                         'amount' : amount,
                         'currency_id' : currency_id,
                         'remarks' : self.remarks,
                         'from_date' : self.from_date,
                         'to_date' : self.to_date})
        data.update({'get_data': main_lst})
        data.update(self.read([])[0])
        return self.env['report'].get_action([], 'modifier_teo_sale_order.so_line_report', data=data)
