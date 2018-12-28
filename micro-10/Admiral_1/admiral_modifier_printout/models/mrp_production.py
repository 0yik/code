# -*- coding: utf-8 -*-
import StringIO
import base64

import datetime
import xlsxwriter
from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def get_data_shortage(self):
        data = []
        mo_ids = self.search([('procurement_group_id','!=', False)])
        so_obj = self.env['sale.order']
        mrp_bom = self.env['mrp.bom']
        num = 1
        for mo in mo_ids:
            if mo.procurement_group_id:
                so = so_obj.search([('procurement_group_id','=',mo.procurement_group_id.id)])
                for line in so.order_line:
                    mrp_bom_obj = mrp_bom.search([('product_id', '=', line.product_id.id), ('company_id', '=', so.company_id.id)])

                    if not mrp_bom_obj:
                        mrp_bom_obj = mrp_bom.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                                      ('company_id', '=', so.company_id.id)])
                    qty_ordered = 0
                    etd = ''
                    for obj in mrp_bom_obj:
                        for bom_line in obj.bom_line_ids:
                            required_production = line.product_uom_qty - line.product_id.qty_available
                            if required_production > 0:
                                material_for_one_product = bom_line.product_qty / bom_line.bom_id.product_qty
                                if bom_line.product_id.qty_available < (material_for_one_product * required_production):
                                    shortage = (material_for_one_product * line.product_uom_qty) - bom_line.product_id.qty_available
                                    for procurement in mo.procurement_group_id.procurement_ids:
                                        if procurement.purchase_id and procurement.purchase_line_id and procurement.purchase_line_id.product_id == bom_line.product_id:
                                            qty_ordered = procurement.purchase_line_id.product_qty
                                            etd = procurement.purchase_line_id.date_planned
                                    shortage_list = {
                                        'number': num,
                                        'date'  : datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                        'material_code' : bom_line.product_id.barcode or '',
                                        'material_name' : bom_line.product_id.name or '',
                                        'qty_avail'     : bom_line.product_id.qty_available,
                                        'qty_shortage'  : shortage,
                                        'so'            : so.name,
                                        'po_date'       : line.order_id.date_order,
                                        'reason_code'   : '',
                                        'fg_code'       : line.product_id.barcode or '',
                                        'description'   : line.name,
                                        'qty_ordered'   : qty_ordered,
                                        'etd'           : etd,
                                    }
                                    data.append(shortage_list)
                                    num +=1
        return data



    def download_material_shortage_to_excel(self):
        shortages = self.get_data_shortage()
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Material Shortage Rpt')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold': 1, 'bg_color': 'yellow', 'font_size': 14, 'border': 1, 'align': 'center'})

        # Generate 1st row.

        worksheet.write(row, col, unicode('S/No', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Material Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Name', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Qty Avail', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Qty Shortage', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Reason Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('PO No Affected', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('PO Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('FG Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Description', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('RM Qty Ordered', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('ETD', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        for shortage in shortages:
            row += 1
            col = 0

            worksheet.write(row, col, shortage.get('number') or '')
            col += 1

            worksheet.write(row, col, shortage.get('date') or '')
            col += 1

            worksheet.write(row, col, shortage.get('material_code') or '')
            col += 1

            worksheet.write(row, col, shortage.get('material_name') or '')
            col += 1

            worksheet.write(row, col, shortage.get('qty_avail'))
            col += 1

            worksheet.write(row, col, shortage.get('qty_shortage'))
            col += 1

            worksheet.write(row, col, shortage.get('reason_code') or '')
            col += 1

            worksheet.write(row, col, shortage.get('so') or '')
            col += 1

            worksheet.write(row, col, shortage.get('po_date') or '')
            col += 1

            worksheet.write(row, col, shortage.get('fg_code') or '')
            col += 1

            worksheet.write(row, col, shortage.get('description') or '')
            col += 1

            worksheet.write(row, col, shortage.get('qty_ordered') or '')
            col += 1

            worksheet.write(row, col, shortage.get('etd') or '')
            col += 1

        row += 2
        row += 1

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': 'Material Shortage.xlsx', 'datas_fname': 'Material Shortage.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "self",
        }

    def get_data_capacity_planning(self):
        data = []
        mo_ids = self.search([])
        so_obj = self.env['sale.order']
        num = 1
        for mo in mo_ids:
            if mo.procurement_group_id:
                so = so_obj.search([('procurement_group_id','=',mo.procurement_group_id.id)])
                order_line = so.order_line.filtered(lambda l: l.product_id == mo.product_id)
                if so:
                    for work_order in mo.workorder_ids:
                        if work_order.workcenter_id:
                            capacity_planning_list = {
                                'number'   : num,
                                'date'     : mo.date_planned_start,
                                'vessel'   : work_order.workcenter_id.name or '',
                                'capacity' : work_order.workcenter_id.capacity or '',
                                'so_num'   : so.name,
                                'so_date'  : so.confirmation_date,
                                'fg_code'  : order_line[0].product_id.barcode or '',
                                'description' : order_line[0].name,
                                'mfg_qty'  : mo.product_qty,
                            }
                            data.append(capacity_planning_list)
                            num +=1
        return data


    def download_capacity_planning_to_excel(self):
        mo_ids = self._context.get('active_ids', [])
        # if mo_ids:
        planning_data = self.get_data_capacity_planning()
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Capacity Planning')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold': 1, 'bg_color': 'yellow', 'font_size': 14, 'border': 1, 'align': 'center'})

        # Generate 1st row.

        worksheet.write(row, col, unicode('S/No', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Vessel', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Capacity', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('PO for Mfg', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('PO Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('FG Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Description', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Mfg Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        for plan in planning_data:
            row += 1
            col = 0

            worksheet.write(row, col, plan.get('number') or '')
            col += 1

            worksheet.write(row, col, plan.get('date') or '')
            col += 1

            worksheet.write(row, col, plan.get('vessel') or '')
            col += 1

            worksheet.write(row, col, plan.get('capacity'))
            col += 1

            worksheet.write(row, col, plan.get('so_num') or '')
            col += 1

            worksheet.write(row, col, plan.get('so_date'))
            col += 1

            worksheet.write(row, col, plan.get('fg_code') or '')
            col += 1

            worksheet.write(row, col, plan.get('description') or '')
            col += 1

            worksheet.write(row, col, plan.get('mfg_qty'))
            col += 1
        row += 2
        row += 1

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': 'Capacity Planning.xlsx', 'datas_fname': 'Capacity Planning.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "self",
        }

    def get_data_production_schedule(self):
        data = []
        mo_ids = self.search([('state','=','progress')])
        so_obj = self.env['sale.order']
        num = 1
        for mo in mo_ids:
            if mo.procurement_group_id:
                so = so_obj.search([('procurement_group_id','=',mo.procurement_group_id.id)])
                order_line = so.order_line.filtered(lambda l: l.product_id == mo.product_id)
                if so:
                    for work_order in mo.workorder_ids:
                        if work_order.workcenter_id:
                            schedule_list = {
                                'number'   : num,
                                'date'     : mo.date_planned_start,
                                'vessel'   : work_order.workcenter_id.name or '',
                                'so_num'   : so.name,
                                'so_date'  : so.confirmation_date,
                                'allocation_code' : '',
                                'fg_code'  : order_line[0].product_id.barcode or '',
                                'description' : order_line[0].name,
                                'mfg_qty'  : mo.product_qty,
                            }
                            data.append(schedule_list)
                            num +=1
        return data


    def download_production_schedule_to_excel(self):
        mo_ids = self._context.get('active_ids', [])
        # if mo_ids:
        schedule_data = self.get_data_production_schedule()
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Production Schdedule')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold': 1, 'bg_color': 'yellow', 'font_size': 14, 'border': 1, 'align': 'center'})

        # Generate 1st row.

        worksheet.write(row, col, unicode('S/No', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Vessel', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('PO for Mfg', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('PO Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Allocation Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('FG Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Description', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Mfg Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        for schedule in schedule_data:
            row += 1
            col = 0

            worksheet.write(row, col, schedule.get('number') or '')
            col += 1

            worksheet.write(row, col, schedule.get('date') or '')
            col += 1

            worksheet.write(row, col, schedule.get('vessel') or '')
            col += 1

            worksheet.write(row, col, schedule.get('so_num') or '')
            col += 1

            worksheet.write(row, col, schedule.get('so_date'))
            col += 1

            worksheet.write(row, col, schedule.get('allocation_code'))
            col += 1

            worksheet.write(row, col, schedule.get('fg_code') or '')
            col += 1

            worksheet.write(row, col, schedule.get('description') or '')
            col += 1

            worksheet.write(row, col, schedule.get('mfg_qty'))
            col += 1

        row += 2
        row += 1

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': 'Production Schdedule.xlsx', 'datas_fname': 'Production Schdedule.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "self",
        }

    def get_data_stock_take(self):
        data = []
        stock_take_ids = self.env['stock.inventory'].search([('state','=','done')])
        stock_quant_obj = self.env['stock.quant']
        num = 1
        for stock_take_id in stock_take_ids:
            for line in stock_take_id.line_ids:
                if line.product_id and line.product_id.categ_id and line.product_id.categ_id.name == 'Raw Materials':
                    stock_wh_quants = stock_quant_obj.search([('product_id','=',line.product_id.id),('location_id.name','=','Warehouse')])
                    stock_product_quants = stock_quant_obj.search([('product_id','=',line.product_id.id),('location_id.name','=','Production')])
                    sum_wh_qty = sum(stock.qty for stock in stock_wh_quants)
                    sum_product_qty = sum(stock.qty for stock in stock_product_quants)
                    def_qty = line.product_qty - line.theoretical_qty
                    stock_take_list = {
                        'number' : num,
                        'date'   : stock_take_id.date,
                        'code'   : line.product_id.barcode,
                        'name'   : line.product_id.name,
                        'sys_qty': line.theoretical_qty,
                        'actual_qty' : line.product_qty,
                        'def_qty': def_qty,
                        'def_cost': def_qty*line.product_id.standard_price,
                        'wh_qty' : sum_wh_qty,
                        'pro_qty': sum_product_qty,
                    }
                    data.append(stock_take_list)
                    num += 1
        return data

    def download_stock_take_to_excel(self):
        mo_ids = self._context.get('active_ids', [])
        stock_data = self.get_data_stock_take()
        # if mo_ids:
        output = StringIO.StringIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Stock Take Rpt')
        row = 0
        col = 0
        bold_format = workbook.add_format({'bold': 1, 'bg_color': 'yellow', 'font_size': 14, 'border': 1, 'align': 'center'})

        # Generate 1st row.

        worksheet.write(row, col, unicode('S/No', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Date', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Material Code', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Name', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('System Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Actual Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Deficit Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Deficit (Cost)', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('WH Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        worksheet.write(row, col, unicode('Production Qty', "utf-8"), bold_format)
        worksheet.set_column(row, col, 20)
        col += 1

        for stock in stock_data:
            row += 1
            col = 0

            worksheet.write(row, col, stock.get('number') or '')
            col += 1

            worksheet.write(row, col, stock.get('date') or '')
            col += 1

            worksheet.write(row, col, stock.get('code') or '')
            col += 1

            worksheet.write(row, col, stock.get('name') or '')
            col += 1

            worksheet.write(row, col, stock.get('sys_qty'))
            col += 1

            worksheet.write(row, col, stock.get('actual_qty'))
            col += 1

            worksheet.write(row, col, stock.get('def_qty'))
            col += 1

            worksheet.write(row, col, stock.get('def_cost'))
            col += 1

            worksheet.write(row, col, stock.get('wh_qty'))
            col += 1

            worksheet.write(row, col, stock.get('pro_qty'))
            col += 1

        row += 2
        row += 1

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.create(
            {'name': 'Stock Take Rpt.xlsx', 'datas_fname': 'Stock Take Rpt.xlsx', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "self",
        }