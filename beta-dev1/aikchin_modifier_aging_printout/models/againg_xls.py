# -*- coding: utf-8 -*-
import base64
import cStringIO
from datetime import datetime

import xlwt
from dateutil.relativedelta import relativedelta
from odoo import api, models
from odoo.tools.misc import formatLang
from xlwt import *


class account_aged_trial_balance(models.TransientModel):
    _inherit = "account.aged.trial.balance"

    @api.multi
    def print_aged_xls_report(self):
        ctx = self._context.copy()
        ctx.update({'active_model': 'account.aged.trial.balance', 'active_id': self.id, 'total_account': []})
        partners = {
            'customer': "Receivable Accounts",
            'supplier': "Payable Accounts",
            'customer_supplier': "Receivable and Payable Accounts"
        }

        target = {
            'posted': "All Posted Entries",
            'all': "All Entries",
            'draft': "All Unposted Entries"
        }

        direction = {
            'past': 'Past',
            'future': 'Future'
        }

        fp = cStringIO.StringIO()

        wb = xlwt.Workbook(encoding='utf-8')

        current_obj = self

        header_style = xlwt.XFStyle()
        font = xlwt.Font()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        bg_color = current_obj.xls_theme_id.bg_color or 'black'
        pattern.pattern_fore_colour = xlwt.Style.colour_map[bg_color]
        font.height = int(current_obj.xls_theme_id.font_size)
        font.bold = current_obj.xls_theme_id.font_bold
        font.italic = current_obj.xls_theme_id.font_italic
        font_color = current_obj.xls_theme_id.font_color or 'white'
        font.colour_index = xlwt.Style.colour_map[font_color]
        header_style.pattern = pattern
        header_style.font = font
        al3 = Alignment()
        al3.horz = current_obj.xls_theme_id.header_alignment or 0x02
        header_style.alignment = al3

        column_header_style = xlwt.XFStyle()
        font = xlwt.Font()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        bg_color = current_obj.xls_theme_id.column_bg_color or 'red'
        pattern.pattern_fore_colour = xlwt.Style.colour_map[bg_color]
        font.height = int(current_obj.xls_theme_id.column_font_size)
        font.bold = current_obj.xls_theme_id.column_font_bold
        font.italic = current_obj.xls_theme_id.column_font_italic
        font_color = current_obj.xls_theme_id.column_font_color or 'white'
        font.colour_index = xlwt.Style.colour_map[font_color]
        column_header_style.pattern = pattern
        column_header_style.font = font
        al3 = Alignment()
        al3.horz = current_obj.xls_theme_id.column_header_alignment
        column_header_style.alignment = al3

        body_header_style = xlwt.XFStyle()
        font = xlwt.Font()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        bg_color = current_obj.xls_theme_id.body_bg_color or 'gold'
        pattern.pattern_fore_colour = xlwt.Style.colour_map[bg_color]
        font.height = int(current_obj.xls_theme_id.body_font_size)
        font.bold = current_obj.xls_theme_id.body_font_bold
        font.italic = current_obj.xls_theme_id.body_font_italic
        font_color = current_obj.xls_theme_id.body_font_color or 'white'
        font.colour_index = xlwt.Style.colour_map[font_color]
        body_header_style.pattern = pattern
        body_header_style.font = font
        al3 = Alignment()
        al3.horz = current_obj.xls_theme_id.body_header_alignment
        body_header_style.alignment = al3

        filename = 'Detail Aging Report.xls'
        worksheet = wb.add_sheet('Detail Aging Reportxls')
        worksheet.write_merge(0, 1, 1, 9, "Detail Aging Report", header_style)

        worksheet.write(10, 2, "Partners", column_header_style)

        for i in range(0, 17):
            column = worksheet.col(i)
            column.width = 220 * 25

        worksheet.write(3, 3, 'Start Date', column_header_style)
        worksheet.write(4, 3, current_obj.date_from, body_header_style)

        worksheet.write(3, 4, 'Period Length(days)', column_header_style)
        worksheet.write(4, 4, current_obj.period_length, body_header_style)

        worksheet.write(3, 5, "Partner's", column_header_style)
        worksheet.write(4, 5, partners[current_obj.result_selection], body_header_style)

        worksheet.write(3, 6, 'Target Moves', column_header_style)
        worksheet.write(4, 6, target[current_obj.target_move], body_header_style)

        worksheet.write(11, 1, "Account Total", column_header_style)

        data = {}
        res = {}
        data['form'] = self.read(['date_from', 'target_move', 'result_selection', 'period_length', 'company_id'])[0]
        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        period_length = self.period_length
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (str((5 - (i + 1)) * period_length) + '-' + str((5 - i) * period_length)) or (
                    '+' + str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        date_from = self.date_from
        target_move = self.target_move

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']
        test1 = self.env['report.account.report_agedpartnerbalance']
        total = []
        movelines, total, dummy = self.env['report.account.report_agedpartnerbalance']._get_partner_move_lines(
            account_type, date_from, target_move, data['form']['period_length'])
        if movelines:
            count = 0
            for moveline in movelines:
                partner_id = moveline['partner_id']
                partner_obj = self.sudo().env['res.partner'].browse(partner_id)
                credit_limit = partner_obj.credit_limit
                vendor_payment_id = partner_obj.property_supplier_payment_term_ids
                vendor_payment = [line.name for line in vendor_payment_id]
                customer_payment_id = partner_obj.property_payment_term_ids
                customer_payment = [line.name for line in customer_payment_id]
                payment = customer_payment + vendor_payment
                payment = list(set(payment))
                payment = ', '.join(payment)
                sale = partner_obj.user_id.name
                p_id = partner_obj.customer_id and partner_obj.customer_id or partner_obj.supplier_id
                phone = partner_obj.phone
                vals = {
                    'credit_limit': credit_limit and credit_limit or '',
                    'payment': payment and payment or '',
                    'sale': sale and sale or '',
                    'p_id': p_id and p_id or '',
                    'phone': phone and phone or ''
                }
                movelines[count].update(vals)
                count = count + 1
        worksheet.write(10, 1, 'Partner ID', column_header_style)
        worksheet.write(10, 3, 'Tel', column_header_style)
        worksheet.write(10, 4, 'Salesperson', column_header_style)
        worksheet.write(10, 5, 'Payment Terms', column_header_style)
        worksheet.write(10, 6, 'Credit Limit', column_header_style)
        worksheet.write(10, 7, 'Not Due', column_header_style)
        worksheet.write(10, 8, data['form']['4']['name'], column_header_style)
        worksheet.write(10, 9, data['form']['3']['name'], column_header_style)
        worksheet.write(10, 10, data['form']['2']['name'], column_header_style)
        worksheet.write(10, 11, data['form']['1']['name'], column_header_style)
        worksheet.write(10, 12, data['form']['0']['name'], column_header_style)
        worksheet.write(10, 13, 'Total', column_header_style)
        if movelines:
            worksheet.write(11, 2, "",column_header_style)
            worksheet.write(11, 3, "",column_header_style)
            worksheet.write(11, 4, "",column_header_style)
            worksheet.write(11, 5, "",column_header_style)
            worksheet.write(11, 6, "",column_header_style)
            worksheet.write(11, 7, formatLang(self.env, total[6], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            worksheet.write(11, 8, formatLang(self.env, total[4], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            worksheet.write(11, 9, formatLang(self.env, total[3], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            worksheet.write(11, 10, formatLang(self.env, total[2], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            worksheet.write(11, 11, formatLang(self.env, total[1], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            worksheet.write(11, 12, formatLang(self.env, total[0], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            worksheet.write(11, 13, formatLang(self.env, total[5], currency_obj=current_obj.company_id.currency_id),
                            column_header_style)
            row = 12
        for partner in movelines:
            worksheet.write(row, 1, partner['p_id'], body_header_style)
            worksheet.write(row, 2, partner['name'], body_header_style)
            worksheet.write(row, 3, partner['phone'], body_header_style)
            worksheet.write(row, 4, partner['sale'], body_header_style)
            worksheet.write(row, 5, partner['payment'], body_header_style)
            worksheet.write(row, 6, partner['credit_limit'], body_header_style)
            worksheet.write(row, 7,
                            formatLang(self.env, partner['direction'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            worksheet.write(row, 8, formatLang(self.env, partner['4'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            worksheet.write(row, 9, formatLang(self.env, partner['3'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            worksheet.write(row, 10,
                            formatLang(self.env, partner['2'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            worksheet.write(row, 11,
                            formatLang(self.env, partner['1'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            worksheet.write(row, 12,
                            formatLang(self.env, partner['0'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            worksheet.write(row, 13,
                            formatLang(self.env, partner['total'], currency_obj=current_obj.company_id.currency_id),
                            body_header_style)
            row = row + 1
        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        final_arr_data = {}
        final_arr_data['file_stream'] = out
        final_arr_data['name'] = filename

        crete_id = self.env['account.report.view'].create(final_arr_data)
        return {
            'nodestroy': True,
            'res_id': crete_id.id,
            'name': filename,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.report.view',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


account_aged_trial_balance()
