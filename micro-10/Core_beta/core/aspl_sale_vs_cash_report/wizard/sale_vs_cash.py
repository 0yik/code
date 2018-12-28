# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, fields, api,_
from openerp.exceptions import Warning
from datetime import datetime, date, timedelta
import dateutil.relativedelta
import time
import calendar
import logging

_logger = logging.getLogger(__name__)


try:
   import xlwt
except ImportError:
   _logger.debug('Cannot `import xlwt`.')
try:
   import cStringIO
except ImportError:
   _logger.debug('Cannot `import cStringIO`.')
try:
   import base64
except ImportError:
   _logger.debug('Cannot `import base64`.')


class wizard_sale_cash_reports(models.TransientModel):
    _name = "wizard.sale.cash.reports"

    to_date = fields.Date(string="To Date", default=datetime.today())
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    data = fields.Binary('File')
    name = fields.Char('Name')
    from_date = fields.Date(string="From Date")

    @api.multi
    def action_print(self):
        today = datetime.now().strftime("%Y-%m-%d")
        date = self.to_date if self.to_date else today
        to_date = datetime.strptime(date,'%Y-%m-%d')
        acc_rec_typ = self.env['account.account.type'].search([('type', '=', 'receivable'),
                                                               ])
        acc_qry = self.env['account.account'].search([('user_type_id', '=', acc_rec_typ.id)]).ids
        filtered_partner_ids = []
        sql = """select distinct aml.partner_id,rp.name
                        from account_move_line aml, account_move am, res_partner rp 
                        where aml.move_id = am.id AND aml.partner_id = rp.id AND am.state = 'posted'
                        AND aml.account_id in %s 
                        AND aml.date <= '%s'
                        order by rp.name
                         """%("(%s) " % ','.join(map(str, acc_qry)),
                              date)
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        for eb in res:
            if eb.get('partner_id'):
                filtered_partner_ids.append(eb.get('partner_id'))
        lst_slots_dates = []
        lst_slots_dates.append(str(to_date.date()))
        final_result = []
        current_month = to_date.strftime("%B")
        first_prev = to_date + dateutil.relativedelta.relativedelta(months=-1)
        last_prev_day = first_prev.replace(day = calendar.monthrange(first_prev.year, first_prev.month)[1])
        lst_slots_dates.append(str(last_prev_day.date()))
        first_prev_name = first_prev.strftime("%B")
        second_prev = to_date + dateutil.relativedelta.relativedelta(months=-2)
        second_prev_name = second_prev.strftime("%B")
        second_prev_l_day = second_prev.replace(day = calendar.monthrange(second_prev.year, second_prev.month)[1])
        lst_slots_dates.append(str(second_prev_l_day.date()))
        third_prev = to_date + dateutil.relativedelta.relativedelta(months=-3)
        third_prev_l_day = third_prev.replace(day = calendar.monthrange(third_prev.year, third_prev.month)[1])
        lst_slots_dates.append(str(third_prev_l_day.date()))
        third_prev_name = third_prev.strftime("%B")
        list_months = [to_date.month,first_prev.month,second_prev.month,third_prev.month]
#         list_months_copy = [to_date.month,first_prev.month,second_prev.month,third_prev.month]
        for ep in filtered_partner_ids:
            main_dict = {}
#             partner_id = self.env['res.partner'].browse([ep])
#             partner_name = partner_id.id if partner_id a else partner_id.parent_id.name
            for each_index in range(0, len(lst_slots_dates)):
                sql1 = """select aml.partner_id, sum(aml.debit) as debit
                            from account_move_line aml, account_move am 
                            where aml.move_id = am.id AND am.state = 'posted'
                            AND aml.account_id in %s 
                            AND aml.partner_id = %s
                             """%("(%s) " % ','.join(map(str, acc_qry)),
                                  ep)
                if each_index != len(lst_slots_dates) - 1:
                    sql1 += """ AND aml.date::timestamp::date <= '%s' AND
                                aml.date::timestamp::date > '%s'""" % (lst_slots_dates[each_index], lst_slots_dates[each_index + 1])
                else:
                    sql1 += """ AND aml.date::timestamp::date <= '%s'""" % (lst_slots_dates[each_index])
                sql1 +="""GROUP BY aml.partner_id"""
                self._cr.execute(sql1)
                result = self._cr.dictfetchall()
                sql2 = """select aml.partner_id, sum(aml.credit)  as cash_or_bank
                            from account_move_line aml, account_move am ,account_journal aj
                            where aml.move_id = am.id AND am.state = 'posted'
                            AND aj.id = aml.journal_id
                            AND aj.type in ('bank', 'cash')
                            AND aml.account_id in %s
                            AND aml.partner_id = %s
                             """%("(%s) " % ','.join(map(str, acc_qry)),
                                  ep)
                if each_index != len(lst_slots_dates) - 1:
                    sql2 += """ AND aml.date::timestamp::date <= '%s' AND
                                aml.date::timestamp::date > '%s'""" % (lst_slots_dates[each_index], lst_slots_dates[each_index + 1])
                else:
                    sql2 += """ AND aml.date::timestamp::date <= '%s'""" % (lst_slots_dates[each_index])
                sql2 +="""GROUP BY aml.partner_id"""
                self._cr.execute(sql2)
                result2 = self._cr.dictfetchall()
                sql3 = """select aml.partner_id, sum(aml.credit)  as credit_sum
                            from account_move_line aml, account_move am ,account_journal aj
                            where aml.move_id = am.id AND am.state = 'posted'
                            AND aj.id = aml.journal_id
                            AND aml.account_id in %s
                            AND aml.partner_id = %s
                             """%("(%s) " % ','.join(map(str, acc_qry)),
                                  ep)
                if each_index != len(lst_slots_dates) - 1:
                    sql3 += """ AND aml.date::timestamp::date <= '%s' AND
                                aml.date::timestamp::date > '%s'""" % (lst_slots_dates[each_index], lst_slots_dates[each_index + 1])
                else:
                    sql3 += """ AND aml.date::timestamp::date <= '%s'""" % (lst_slots_dates[each_index])
                sql3 +="""GROUP BY aml.partner_id"""
                self._cr.execute(sql3)
                result3 = self._cr.dictfetchall()
                main_dict[list_months[each_index]] = [{ep:{'sales': result[0]['debit'] if result and result[0]['debit'] else 0.00,
                                                                     'cash': result2[0]['cash_or_bank'] if result2 and result2[0]['cash_or_bank'] else 0.00,
                                                                     'credit': result3[0]['credit_sum'] if result3 and result3[0]['credit_sum'] else 0.00,
                                                                     }}]
            final_result.append({ep:main_dict})
        stylePC = xlwt.XFStyle()
        styledata = xlwt.XFStyle()
        styletotal = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignmentr = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_LEFT
        alignmentr.horz = xlwt.Alignment.HORZ_RIGHT
        fontP = xlwt.Font()
        fontd = xlwt.Font()
        fontt = xlwt.Font()
        fontP.bold = True
        fontt.bold = True
        fontd.bold = False
        stylePC.font = fontP
        stylePC.alignment = alignment
        styletotal.font = fontt
        styletotal.alignment = alignmentr
        styledata.font = fontd
        styledata.alignment = alignmentr
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet("Report")
        worksheet.write_merge(2, 2, 0, 0, 'Customers', style=stylePC)
        a = 3
        sale = 0.0
        credit = 0.0
        cash = 0.0
        sale_second = 0.0
        credit_second = 0.0
        cash_second = 0.0
        sale_third = 0.0
        credit_third = 0.0
        cash_third = 0.0
        sale_fourth = 0.0
        credit_fourth = 0.0
        cash_fourth = 0.0
        for every in final_result:
            for key,value in every.iteritems():
                temp_total = 0.0
                partner_name = self.env['res.partner'].browse([key]).name
                worksheet.write_merge(a, a, 0, 0, partner_name, style=stylePC)
                b = 1
                d = 3
                c = 2
                e = 4
                credit_amt = 0.00
                for ky,val in value.iteritems():
                    worksheet.write_merge(a, a, b, b, "%.2f" %(val[0].get(key).get('sales')), style=styledata)
                    worksheet.write_merge(a, a, d, d, "%.2f" %(val[0].get(key).get('cash')), style=styledata)
                    if not val[0].get(key).get('cash') and not val[0].get(key).get('credit'):
                        worksheet.write_merge(a, a, c, c, 0.00, style=styledata)
                        credit_amt = 0.00
                    elif not val[0].get(key).get('cash') and val[0].get(key).get('credit'):
                        worksheet.write_merge(a, a, c, c, val[0].get(key).get('credit'), style=styledata)
                        credit_amt = float("%.2f" %val[0].get(key).get('credit'))
                    elif not val[0].get(key).get('cash'):
                        worksheet.write_merge(a, a, c, c, 0.00, style=styledata)
                    elif val[0].get(key).get('credit_amt') == val[0].get(key).get('cash'):
                        worksheet.write_merge(a, a, c, c, 0.00, style=styledata)
                    else:
                        worksheet.write_merge(a, a, c, c, val[0].get(key).get('credit') - val[0].get(key).get('cash'), style=styledata)
                        credit_amt = val[0].get(key).get('credit') - val[0].get(key).get('cash')
                    temp_total += val[0].get(key).get('sales') - credit_amt - val[0].get(key).get('cash')
                    worksheet.write_merge(a, a, e, e, "%.2f" %(temp_total), style=styletotal)
                    if list_months.index(ky) == 3:
                        sale+=val[0].get(key).get('sales')
                        cash+=val[0].get(key).get('cash')
                        credit+=credit_amt
                    if list_months.index(ky) == 2:
                        sale_second+=val[0].get(key).get('sales')
                        cash_second+=val[0].get(key).get('cash')
                        credit_second+=credit_amt
                        
                    if list_months.index(ky) == 1:
                        sale_third+=val[0].get(key).get('sales')
                        cash_third+=val[0].get(key).get('cash')
                        credit_third+=credit_amt
                    if list_months.index(ky) == 0:
                        sale_fourth+=val[0].get(key).get('sales')
                        cash_fourth+=val[0].get(key).get('cash')
                        credit_fourth+=credit_amt
                    b += 5
                    c += 5
                    d += 5
                    e += 5
                a+=1
        fisrt_tot = sale - credit - cash
        second_tot = fisrt_tot + (sale_second - credit_second - cash_second)
        third_tot = second_tot + (sale_third - credit_third - cash_third)
        fourth_tot = third_tot + (sale_fourth - credit_fourth - cash_fourth)
        worksheet.write_merge(2, 2, 1, 1, sale, style=styletotal)
        worksheet.write_merge(2, 2, 2, 2, credit, style=styletotal)
        worksheet.write_merge(2, 2, 3, 3, cash, style=styletotal)
        worksheet.write_merge(2, 2, 4, 4, fisrt_tot, style=styletotal)
        worksheet.write_merge(2, 2, 6, 6, sale_second, style=styletotal)
        worksheet.write_merge(2, 2, 7, 7, credit_second, style=styletotal)
        worksheet.write_merge(2, 2, 8, 8, cash_second, style=styletotal)
        worksheet.write_merge(2, 2, 9, 9, second_tot, style=stylePC)
        worksheet.write_merge(2, 2, 11, 11, sale_third, style=styletotal)
        worksheet.write_merge(2, 2, 12, 12, credit_third, style=styletotal)
        worksheet.write_merge(2, 2, 13, 13, cash_third, style=styletotal)
        worksheet.write_merge(2, 2, 14, 14, third_tot, style=stylePC)
        worksheet.write_merge(2, 2, 16, 16, sale_fourth, style=styletotal)
        worksheet.write_merge(2, 2, 17, 17, credit_third, style=styletotal)
        worksheet.write_merge(2, 2, 18, 18, cash_third, style=styletotal)
        worksheet.write_merge(2, 2, 19, 19, fourth_tot, style=stylePC)
        worksheet.write_merge(0, 0, 16, 20, current_month, style=stylePC)
        worksheet.write_merge(0, 0, 11, 15, first_prev_name, style=stylePC)
        worksheet.write_merge(0, 0, 6, 10, second_prev_name, style=stylePC)
        worksheet.write_merge(0, 0, 1, 5, third_prev_name, style=stylePC)
        worksheet.write_merge(1, 1, 0, 0, ' ', style=stylePC)
        worksheet.write_merge(1, 1, 1, 1, 'Sales', style=stylePC)
        worksheet.write_merge(1, 1, 2, 2, 'Credits', style=stylePC)
        worksheet.write_merge(1, 1, 3, 3, 'Cash', style=stylePC)
        worksheet.write_merge(1, 1, 4, 4, 'Total', style=stylePC)
        worksheet.write_merge(1, 1, 5, 5, ' ', style=stylePC)
        worksheet.write_merge(1, 1, 6, 6, 'Sales', style=stylePC)
        worksheet.write_merge(1, 1, 7, 7, 'Credits', style=stylePC)
        worksheet.write_merge(1, 1, 8, 8, 'Cash', style=stylePC)
        worksheet.write_merge(1, 1, 9, 9, 'Total', style=stylePC)
        worksheet.write_merge(1, 1, 10, 10, ' ', style=stylePC)
        worksheet.write_merge(1, 1, 11, 11, 'Sales', style=stylePC)
        worksheet.write_merge(1, 1, 12, 12, 'Credits', style=stylePC)
        worksheet.write_merge(1, 1, 13, 13, 'Cash', style=stylePC)
        worksheet.write_merge(1, 1, 14, 14, 'Total', style=stylePC)
        worksheet.write_merge(1, 1, 15, 15, ' ', style=stylePC)
        worksheet.write_merge(1, 1, 16, 16, 'Sales', style=stylePC)
        worksheet.write_merge(1, 1, 17, 17, 'Credits', style=stylePC)
        worksheet.write_merge(1, 1, 18, 18, 'Cash', style=stylePC)
        worksheet.write_merge(1, 1,19, 19, 'Total', style=stylePC)
        worksheet.write_merge(1, 1, 20, 20, ' ', style=stylePC)
        worksheet.col(0).width = 10000
        width = 4200
        file_data = cStringIO.StringIO()
        workbook.save(file_data)
        self.write({
            'state': 'get',
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'Sales vs Cash.xls'
        })
        return {
            'name': 'Sales vs Cash Report',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.sale.cash.reports',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: