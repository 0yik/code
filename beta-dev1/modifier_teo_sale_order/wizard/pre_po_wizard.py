# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math, time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class PrePOWizard(models.TransientModel):
    _name = 'pre.po.wizard'
    
    remarks = fields.Html("Remarks")
    
    @api.multi
    def create_pre_po(self):
        data = {}
        main_data = []
        summary_lst = [] 
        active_line = self.env['sale.order.line'].browse(self._context.get('active_ids', []))
        style_lst = list(set([x.product_id for x in active_line]))
        colour_lst = list(set([x.col_code for x in active_line]))
        size_list = []
        uom_lst = list(set([x.product_uom for x in active_line]))
        for line in active_line:
            size = [str(x.size) for x in line.size_line]
            if size not in size_list:
                size_list.append(size)
        filter_list = []
        for style in style_lst:
            style_line = []
            for line in active_line:
                if line.product_id == style:
                    style_line.append(line)
            filter_list.append(style_line)
        for so_line_list in filter_list:
            main_lst = []
            customer_lst = list(set([x.order_id.partner_id for x in so_line_list]))
            shipment_list = list(set([x.shipment_buyer_order_no for x in so_line_list]))
            for shipment in shipment_list:
                for customer in customer_lst:
                    line_lst = []
                    for line in so_line_list:
                        if line.shipment_buyer_order_no == shipment and line.order_id.partner_id == customer:
                            line_dict = {'colour_name': line.colour_name,
                                         'col_code': line.col_code,
                                         'col_name' : [line.col1_name, line.col2_name, line.col3_name],
                                         'col_content' : [line.col1_content, line.col2_content, line.col3_content],
                                         'carton_quantity' : line.ttl_ctn if not line.solid_size_pack else 0,
                                         'pack': line.product_pack_id.name,
                                         'pack_method': line.solid_size_pack,
                                         'ttl_ctn': line.ttl_ctn,
                                         'ratio': line.ratio,
                                         'size': [float(x.qty) for x in line.size_line],
                                         'size_name': [str(x.size) for x in line.size_line],
                                         'total': line.product_uom_qty,
                                         'delivery_date': line.shipment_delivery_date,
                                         'final_destination': line.final_destination,
                                         }
                            line_lst.append(line_dict)
                    line_lst = sorted(line_lst, key=lambda k: k['pack'])
                
                    for size in size_list:
                        total_carton_qty = 0.0
                        size_1 = 0.0
                        size_2 = 0.0
                        size_3 = 0.0
                        size_4 = 0.0
                        size_5 = 0.0
                        size_6 = 0.0
                        size_7 = 0.0
                        size_8 = 0.0
                        size_9 = 0.0
                        total_qty = 0.0
                        final_list = []
                        col_name = []
                        for line in line_lst:
                            if line['size_name'] == size:
                                total_carton_qty += line['carton_quantity']
                                col_list = [x for x in col_name if x != False]
                                col_name = [x for x in line['col_name'] if x != False] if [x for x in line['col_name'] if x != False] > col_list else col_list
                                total_qty += line['total']
                                size_lst = [x for x in line['size']]
                                size_1 += float(size_lst[0]) if len(size_lst) > 0 else 0.0
                                size_2 += float(size_lst[1]) if len(size_lst) > 1 else 0.0
                                size_3 += float(size_lst[2]) if len(size_lst) > 2 else 0.0
                                size_4 += float(size_lst[3]) if len(size_lst) > 3 else 0.0
                                size_5 += float(size_lst[4]) if len(size_lst) > 4 else 0.0
                                size_6 += float(size_lst[5]) if len(size_lst) > 5 else 0.0
                                size_7 += float(size_lst[6]) if len(size_lst) > 6 else 0.0
                                size_8 += float(size_lst[7]) if len(size_lst) > 7 else 0.0
                                size_9 += float(size_lst[8]) if len(size_lst) > 8 else 0.0
                                final_list.append(line)
                        if final_list:
                            main_lst.append({'so_id':shipment,
                                             'total_carton_qty':total_carton_qty,
                                             'total_qty':total_qty,
                                             'size': size,
                                             'col_name': col_name,
                                             'size_1':size_1,
                                             'size_2':size_2,
                                             'size_3':size_3,
                                             'size_4':size_4,
                                             'size_5':size_5,
                                             'size_6':size_6,
                                             'size_7':size_7,
                                             'size_8':size_8,
                                             'size_9':size_9,
                                             'customer':customer.name,
                                             'line_ids':final_list,
                                             'delivery_date':final_list[0].get('delivery_date'),
                                             'final_destination':final_list[0].get('final_destination')})
            main_lst = sorted(main_lst, key=lambda k: (k['delivery_date'], k['customer'], k['final_destination']))
            main_data.append({'style': so_line_list[0].product_id.name,
                              'description': so_line_list[0].name,
                              'get_data': main_lst})
        for size in size_list:
            for uom in uom_lst:
                final_summary_list = []
                for line in active_line:
                    if [str(x.size) for x in line.size_line] == size and line.product_uom == uom:
                        line_dict = {'colour_name': line.colour_name,
                                     'col_code': line.col_code,
                                     'uom': uom.name,
                                     'size': [float(x.qty) for x in line.size_line],
                                     'total': line.product_uom_qty,
                                     }
                        final_summary_list.append(line_dict)
                
                main_summary_list = []
                for colour in colour_lst:
                    summary_list = []
                    for final in final_summary_list:
                        if final['col_code'] == colour:
                            summary_list.append(final)
                    if summary_list:
                        final_size = [sum(i) for i in zip(*[x['size'] for x in summary_list])]
                        final_dict = {'colour_name': summary_list[0]['colour_name'],
                                      'col_code': summary_list[0]['col_code'],
                                     'uom': summary_list[0]['uom'],
                                     'size': final_size,
                                     'total': sum(final_size),
                                     }
                        main_summary_list.append(final_dict)

                size_1 = 0.0
                size_2 = 0.0
                size_3 = 0.0
                size_4 = 0.0
                size_5 = 0.0
                size_6 = 0.0
                size_7 = 0.0
                size_8 = 0.0
                size_9 = 0.0
                total_qty = 0.0
                if main_summary_list:
                    total_qty += sum([x['total'] for x in main_summary_list])
                    size_lst = [x['size'] for x in main_summary_list]
                    for size_n in size_lst:
                        size_1 += float(size_n[0]) if len(size_n) > 0 else 0.0
                        size_2 += float(size_n[1]) if len(size_n) > 1 else 0.0
                        size_3 += float(size_n[2]) if len(size_n) > 2 else 0.0
                        size_4 += float(size_n[3]) if len(size_n) > 3 else 0.0
                        size_5 += float(size_n[4]) if len(size_n) > 4 else 0.0
                        size_6 += float(size_n[5]) if len(size_n) > 5 else 0.0
                        size_7 += float(size_n[6]) if len(size_n) > 6 else 0.0
                        size_8 += float(size_n[7]) if len(size_n) > 7 else 0.0
                        size_9 += float(size_n[8]) if len(size_n) > 8 else 0.0
                    summary_lst.append({'total_qty':total_qty,
                                     'size': size,
                                     'uom': uom.name,
                                     'size_1':size_1,
                                     'size_2':size_2,
                                     'size_3':size_3,
                                     'size_4':size_4,
                                     'size_5':size_5,
                                     'size_6':size_6,
                                     'size_7':size_7,
                                     'size_8':size_8,
                                     'size_9':size_9,
                                     'line_ids':main_summary_list})
        data.update({'main_data': sorted(main_data, key=lambda k: k['style']), 'remarks': self.remarks, 'summary_data': summary_lst, 'style_image':[x.image_medium for x in style_lst], 'revision_date': datetime.now().strftime("%Y-%m-%d"), 'date': active_line[0].order_id.date_order.split(' ')[0] if active_line[0].order_id.date_order else '-'})
        data.update(self.read([])[0])
        return self.env['report'].get_action([], 'modifier_teo_sale_order.pre_po_report', data=data)
