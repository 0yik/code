# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import calendar

class summary_report_wizard(models.TransientModel):
    _name = 'summary.report.wizard'

    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')

# base on purchase order report

    @api.multi
    def get_purchase_data(self):
        # Purchase calculation
        purchase_ids = self.env['purchase.order'].search(
            [('date_order', '>=', self.date_start), ('date_order', '<=', self.date_end)])
        purchase_order_line_ids = self.env['purchase.order.line'].search([('order_id','in',purchase_ids.ids)])

        main_dict = {}
        monthly_sale = []
        total_sale = []
        for line in purchase_order_line_ids:
            # Monthly sales calculation
            today = datetime.now()
            year = today.year
            month = today.month
            monthrange = calendar.monthrange(year, month)
            monthly_sale_ids = self.env['sale.order'].with_context(location_id=line.order_id.picking_type_id.default_location_dest_id.id).search(
                [('product_id', '=', line.product_id.id), ('confirmation_date', '>=', self.date_start),
                 ('confirmation_date', '<=', self.date_end)])
            monthly_amount = 0.00
            for monthly_sale_id in monthly_sale_ids:
                if monthly_sale_id not in monthly_sale:
                    monthly_sale.append(monthly_sale_id)
                    monthly_amount += monthly_sale_id.amount_untaxed

            # Total sales calculation
#             total_sale_ids = self.env['sale.order'].with_context(location_id=line.order_id.picking_type_id.default_location_dest_id.id).search(
#                 [('product_id', '=', line.product_id.id), ('confirmation_date', '>=', self.date_start),
#                  ('confirmation_date', '<=', self.date_end)])
            total_sale_ids = self.env['sale.order'].with_context(location_id=line.order_id.picking_type_id.default_location_dest_id.id).search(
                [('product_id', '=', line.product_id.id)])

            total_amount = 0.00
            for total_sale_id in total_sale_ids:
                if total_sale_id not in total_sale:
                    total_sale.append(total_sale_id)
                    total_amount += total_sale_id.amount_untaxed

            # Getting min qty
            min_qty = 0.00
            reordering_ids = self.env['stock.warehouse.orderpoint'].search(
                [('product_id', '=', line.product_id.id), ('location_id', '=', line.order_id.picking_type_id.default_location_dest_id.id)])
            for reordering_id in reordering_ids:
                min_qty += reordering_id.product_min_qty

            # Buffer percentage calculation
            stock_moves_ids = self.env['stock.move'].search(
                [('product_id', '=', line.product_id.id), ('origin', '=', line.order_id.name), ('location_dest_id', '=', line.order_id.picking_type_id.default_location_dest_id.id)])
            buffer = 0.00
            for stock_moves_id in stock_moves_ids:
                buffer += stock_moves_id.buffer_percentage
            if line.product_id.id not in main_dict:
                main_dict.update({line.product_id.id: [{'product': line.product_id.name, 'price': line.product_id.standard_price, 'location_id': line.order_id.picking_type_id.default_location_dest_id.id, 'location': line.order_id.picking_type_id.default_location_dest_id.location_id.name + '/' + line.order_id.picking_type_id.default_location_dest_id.name,
                                                        'total_stock': line.product_id.with_context({'location': line.order_id.picking_type_id.default_location_dest_id.id}).qty_available, 'minimum_qty': min_qty, 'buffer_lead': buffer, 'total_sales': total_amount, 'monthly_sales': monthly_amount}]})
            else:
                location_check = False
                row_count = 0
                for data in main_dict.get(line.product_id.id):
                    if line.order_id.picking_type_id.default_location_dest_id.id == data.get('location_id'):
                        monthly_sales = main_dict.get(line.product_id.id)[row_count].get('monthly_sales')
                        total_sales = main_dict.get(line.product_id.id)[row_count].get('total_sales')
                        buffer_lead = main_dict.get(line.product_id.id)[row_count].get('buffer_lead')
                        main_dict.get(line.product_id.id)[row_count].update({
                            'monthly_sales': monthly_sales + monthly_amount,
                            'total_sales': total_sales + total_amount,
                            'buffer_lead': buffer_lead + buffer
                        })
                        location_check = True
                        break
                    row_count += 1
                if not location_check:
                    main_dict[line.product_id.id].append({
                        'product': line.product_id.name,
                        'price': line.product_id.standard_price,
                        'location_id': line.order_id.picking_type_id.default_location_dest_id.id,
                        'location': line.order_id.picking_type_id.default_location_dest_id.location_id.name + '/' + line.order_id.picking_type_id.default_location_dest_id.name,
                        'total_stock': line.product_id.with_context({'location': line.order_id.picking_type_id.default_location_dest_id.id}).qty_available,
                        'minimum_qty': min_qty,
                        'buffer_lead': buffer,
                        'total_sales': total_amount,
                        'monthly_sales': monthly_amount
                    })

        return main_dict

    @api.multi
    def generate_purchase_report(self):
        return self.env['report'].get_action(self,'pdp_summary_purchase_report.report_summary')


summary_report_wizard()