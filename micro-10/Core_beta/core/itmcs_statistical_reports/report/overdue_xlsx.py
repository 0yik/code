from odoo.addons.itmcs_statistical_reports.report.report_xlsx import ReportXlsx
from datetime import datetime
from PIL import Image

class OverdueReportXls(ReportXlsx):


    def generate_xlsx_report(self, workbook, data, lines):
        report_records = data['form']['context']
        partner_obj = self.env['res.partner']
        overdue_obj = self.env['overdue.report']
        sheet = workbook.add_worksheet('Overdue Info')
        company_header = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12,
                                        'bg_color': data['form']['company_header_bgcolor'],'font_color': data['form']['company_header_fontcolor']})
        report_header = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True,
                                        'bg_color': data['form']['report_header_bgcolor'], 'font_size': 11,'font_color': data['form']['report_header_fontcolor']})
        title_color= workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'bold': True ,
                                           'bg_color': data['form']['title_bgcolor'],'font_color': data['form']['title_fontcolor']})
        subtitle_color = workbook.add_format({'font_size': 10, 'bottom': True, 'right': True, 'left': True, 'top': True,'bold' : True,
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
        sheet.insert_image('B2', 'images.jpg')
        sheet.merge_range('A1:G1', "Company : " + data['form']['company'], company_header)
        if data['form']['select_report'] == 'general':
            sheet.merge_range('A3:G3', 'General Due Sales Report', report_header)
        elif data['form']['select_report'] == 'pos':
            sheet.merge_range('A3:G3', 'Pos Due Sales Report ', report_header)
        else:
            sheet.merge_range('A3:G3', 'Total Due SalesReport ', report_header)
        sheet.merge_range('A4:G4', "From " + start_date + " To " + end_date, report_header)
        
        rows = 5
        for report_record in report_records:
            sheet.merge_range(rows, 0, rows, 5, "Customer :" + partner_obj.browse(report_record[0]).name, title_color)
            rows +=1
            sheet.write(rows, 1, "Customer Invoice", subtitle_color)
            sheet.write(rows, 2, "Overdue Amount", subtitle_color)
            overdue = overdue_obj.browse(report_record[1])
            rows += 1
            total= 0.0
            rows = rows
            for j in overdue:
                sheet.write(
                    rows, 1, j.ref, text_color)
                sheet.write_number(
                    rows, 2,  j.residual, text_color)
                total+= j.residual
                rows += 1
            sheet.write(
                        rows, 1, 'Total Amount', subtitle_color)
            sheet.write_number(
                        rows, 2,total, subtitle_color )
            rows += 2
            
OverdueReportXls('report.itmcs_statistical_reports.overdue_analysis.xlsx', 'overdue.wizard')
