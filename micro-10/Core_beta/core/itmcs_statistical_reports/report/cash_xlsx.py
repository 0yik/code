from odoo.addons.itmcs_statistical_reports.report.report_xlsx import ReportXlsx
from datetime import datetime

# cash ledger report xls file
class CashReportXls(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):
        report_records = data['form']['context']
        account_obj = self.env['account.account']
        sheet = workbook.add_worksheet('Cash Info')
        company_header = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12,
                                        'bg_color': data['form']['company_header_bgcolor'],'font_color': data['form']['company_header_fontcolor']})
        report_header = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True,
                                        'bg_color': data['form']['report_header_bgcolor'], 'font_size': 11,'font_color': data['form']['report_header_fontcolor']})
        title_color= workbook.add_format({'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'top': True, 'bold': True ,
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
        sheet.merge_range('A1:G1', "Company : " + data['form']['company'], company_header)
        
        sheet.merge_range('A3:G3', 'Cash Ledger', report_header)
        sheet.merge_range('A4:G4', "From " + start_date + " To " + end_date, report_header)
        rows = 5
        sheet.write(rows, 0, "Opening Balance", title_color)
        sheet.write_number(
                    rows, 1, report_records['opening_balance_receipt'],title_color)
        
        
        rows = 7
       
        sheet.write(rows, 0, "Receipt", title_color)
        rows += 1
        total= 0.0
        if report_records.get('receipt'):
            
            sheet.write(
                rows, 0, "Account Name", subtitle_color)
            sheet.write(rows, 1, "Amount", subtitle_color)
            sheet.write(rows, 2, "Balance", subtitle_color)
            rows += 1
            rows = rows
            for j in report_records.get('receipt'):
                account_name = account_obj.browse(j.get('account_id'))
                sheet.write(
                    rows, 0, account_name.name, text_color)
                sheet.write_number(
                    rows, 1, j.get('amount'), text_color)
                total+= j.get('amount')
                sheet.write_number(
                    rows, 2, total, text_color)
                 
                rows += 1
            sheet.write(
                        rows, 1, 'Total Receipt', subtitle_color)
            sheet.write_number(
                        rows, 2, total, subtitle_color)
        rows += 2
        sheet.write(rows, 0, "Payment", title_color)
        rows += 1
        total_payment= 0.0
        if report_records.get('payment'):
            sheet.write(
                rows, 0, "Account Name", subtitle_color)
            sheet.write(rows, 1, "Amount", subtitle_color)
            sheet.write(rows, 2, "Balance", subtitle_color)
            rows += 1
            rows = rows
            for j in report_records.get('payment'):
                account_name = account_obj.browse(j.get('account_id'))
                sheet.write(
                    rows, 0, account_name.name, text_color)
                sheet.write_number(
                    rows, 1, j.get('amount') , text_color)
                total_payment+= j.get('amount')
                sheet.write_number(
                    rows, 2, total_payment , text_color)
                 
                rows += 1
            sheet.write(
                        rows, 1, 'Total Payment', subtitle_color)
            sheet.write_number(
                        rows, 2, total, subtitle_color)
        rows += 2
        sheet.write(rows, 1, "Closing Balance", subtitle_color)
        sheet.write_number(
                    rows, 2, report_records['closing_bal_payment'], subtitle_color)
CashReportXls('report.itmcs_statistical_reports.cash_ledger.xlsx', 'cash.ledger.wizard')