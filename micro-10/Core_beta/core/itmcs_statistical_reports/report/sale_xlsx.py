from odoo.addons.itmcs_statistical_reports.report.report_xlsx import ReportXlsx
from datetime import datetime

class SaleReportXls(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):
        report_records = data['form']['context']
        sheet = workbook.add_worksheet('Sale Info')
        company_header = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12,
                                        'bg_color': data['form']['company_header_bgcolor'],'font_color': data['form']['company_header_fontcolor']})
        report_header = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True,
                                        'bg_color': data['form']['report_header_bgcolor'], 'font_size': 11,'font_color': data['form']['report_header_fontcolor']})
        title_color= workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'bold': True ,
                                           'bg_color': data['form']['title_bgcolor'],'font_color': data['form']['title_fontcolor']})
        subtitle_color = workbook.add_format({'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True,'bold': True,  
                                              'bg_color': data['form']['subtitle_bgcolor'],'font_color': data['form']['subtitle_fontcolor']})
        text_color = workbook.add_format({'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True,  
                                              'bg_color': data['form']['text_bgcolor'],'font_color': data['form']['text_fontcolor']})
        report_header.set_align('center')
        company_header.set_align('center')
        title_color.set_align('center')
        subtitle_color.set_align('center')
        text_color.set_align('center')
        start_date = datetime.strptime(data['form']['start_date'], '%Y-%m-%d').strftime('%d/%m/%y')
        end_date = datetime.strptime(data['form']['end_date'], '%Y-%m-%d').strftime('%d/%m/%y')
        sheet.merge_range('A1:I1', "Company : " + data['form']['company'], company_header)
        if data['form']['select_report'] == 'customer':
            sheet.merge_range('A3:I3', 'Sales Analysis - Sales by customer', report_header)
        elif data['form']['select_report'] == 'warehouse':
            sheet.merge_range('A3:I3', 'Warehouse Sales Report - Sales by  warehouse ', report_header)
        sheet.merge_range('A4:I4', "From " + start_date + " To " +end_date, report_header)
        rows = 6
        
        for report_record in report_records:
            if data['form']['select_report'] == 'customer':
                sheet.merge_range(rows, 0, rows, 10, "Customer :" + report_record.get('customer'), title_color)
                rows += 1
                
                sheet.write(
                    rows, 0, "No", subtitle_color)
                sheet.write(rows, 1, "Product Code", subtitle_color)
                sheet.write(rows, 2, "Product Name", subtitle_color)
                sheet.write(rows, 3, "Reference No", subtitle_color)
                sheet.write(rows, 4, "Unit", subtitle_color)
                sheet.write(rows, 5, "Quantity", subtitle_color)
                sheet.write(rows, 6, "Bill Amount", subtitle_color)
                sheet.write(rows, 7, "Sale Price", subtitle_color)
                sheet.write(rows, 8, "Cost Price", subtitle_color)
                sheet.write(rows, 9, "Gross Profit", subtitle_color)
                sheet.write(rows, 10, "Margin (%)", subtitle_color)
                rows += 1
                rows = rows
                no = 1
                total= 0.0
                bill_total= 0.0
                for j in report_record.get('product_data'):
                    sheet.write(rows, 0, no, text_color)
                    no += 1
                    sheet.write(
                        rows, 1, j.get('code'),  text_color)
                    sheet.write(
                        rows, 2, j.get('product_name') , text_color)
                    sheet.write(
                        rows, 3, j.get('ref'), text_color)
                    sheet.write(
                        rows, 4, j.get('uom') , text_color)
                    sheet.write_number(
                        rows, 5, j.get('qty'), text_color)
                    sheet.write_number(
                        rows, 6,j.get('bill_amount'),  text_color)
                    sheet.write_number(
                        rows, 7,j.get('sale_price') , text_color)
                    sheet.write_number(
                        rows, 8, j.get('cost_price') , text_color)
                    sheet.write_number(
                        rows, 9,j.get('gross_profit'), text_color)
                    
                    sheet.write_number(
                        rows, 10, j.get('margin'), text_color)
                    total+= j.get('gross_profit')
                    bill_total+= j.get('bill_amount')
                    rows += 1
                sheet.write(
                        rows, 9, 'Total Gross Profit', subtitle_color)
                sheet.write_number(
                        rows, 10,total, subtitle_color)
                rows += 1
                sheet.write(
                        rows, 9, 'Total Bill Amount', subtitle_color)
                sheet.write_number(
                        rows, 10, bill_total, subtitle_color)
                rows += 2
            
            
            elif data['form']['select_report'] == 'warehouse':
                sheet.merge_range(rows, 0, rows, 9, "warehouse :" + report_record.get('warehouse'), title_color)
                rows += 1
                sheet.write(
                    rows, 0, "No", subtitle_color)
                sheet.write(rows, 1, "Product Code", subtitle_color)
                sheet.write(rows, 2, "Product Name", subtitle_color)
                sheet.write(rows, 3, "Unit", subtitle_color)
                sheet.write(rows, 4, "Quantity", subtitle_color)
                sheet.write(rows, 5, "Bill Amount", subtitle_color)
                sheet.write(rows, 6, "Sale Price", subtitle_color)
                sheet.write(rows, 7, "Cost Price", subtitle_color)
                sheet.write(rows, 8, "Gross Profit", subtitle_color)
                sheet.write(rows, 9, "Margin (%)", subtitle_color)
                rows += 1
                rows = rows
                no = 1
                total= 0.0
                bill_total= 0.0
                for j in report_record.get('product_data'):
                    sheet.write(rows, 0, no, text_color)
                    no += 1
                    sheet.write(
                        rows, 1, j.get('code'),  text_color)
                    sheet.write(
                        rows, 2, j.get('product_name') , text_color)
                    sheet.write(
                        rows, 3, j.get('uom') , text_color)
                    sheet.write_number(
                        rows, 4, j.get('qty'), text_color)
                    sheet.write_number(
                        rows, 5,j.get('bill_amount'),  text_color)
                    sheet.write_number(
                        rows, 6,j.get('sale_price') , text_color)
                    sheet.write_number(
                        rows, 7, j.get('cost_price') , text_color)
                    sheet.write_number(
                        rows, 8,j.get('gross_profit'), text_color)
                    
                    sheet.write_number(
                        rows, 9, j.get('margin'), text_color)
                    total+= j.get('gross_profit')
                    bill_total+= j.get('bill_amount')
                    rows += 1
                sheet.write(
                        rows, 8, 'Total Gross Profit', subtitle_color)
                sheet.write_number(
                        rows, 9,total, subtitle_color)
                rows += 1
                sheet.write(
                        rows, 8, 'Total Bill Amount', subtitle_color)
                sheet.write_number(
                        rows, 9,bill_total, subtitle_color)
                rows += 2
            
SaleReportXls('report.itmcs_statistical_reports.sales_analysis.xlsx', 'custom.wizard')
