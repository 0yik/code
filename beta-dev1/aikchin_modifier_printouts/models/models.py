from odoo import models, fields, api, _
from odoo.tools import amount_to_text_en
import time
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class sale_order_inherit(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('quotaion.order')
        vals['name'] = seq
        return super(sale_order_inherit, self).create(vals)

    def action_confirm(self):
        seq = self.env['ir.sequence'].get('sale.order.aik')
        self['name'] = seq
        res = super(sale_order_inherit, self).action_confirm()

        return res
class acount_invoice_inherit(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        if to_open_invoices.journal_id.code == "INV" and to_open_invoices.journal_id.type == "sale":
            if self.origin != False and self.name != False:
                self.number = self.env['ir.sequence'].get('credit.note')
        if to_open_invoices.journal_id.code == "BILL" and to_open_invoices.journal_id.type == "purchase":
            if self.origin != False and self.name != False:
                self.number = self.env['ir.sequence'].get('debit.note')
        return to_open_invoices.invoice_validate()



class pos_order_inherit(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.model
    def create(self, vals):
        record = super(pos_order_inherit, self).create(vals)
        record['name'] = self.env['ir.sequence'].get('pos.order.format')
        return record

class purchase_order_inherit(models.Model):
    _inherit = 'purchase.order'

    issuer_id = fields.Many2one('hr.employee', 'Issuer', required=True)
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('purchase.order.aik')
        vals['name'] = seq
        return super(purchase_order_inherit, self).create(vals)

class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('stock.picking')
        vals['name'] = seq
        return super(stock_picking_inherit, self).create(vals)

class aikchin_appraisal(models.Model):
    _name =  "aikchin.appraisal"

    name = fields.Char("Name")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    data_list = []

    @api.multi
    def print_appraisal_prinout(self):
        data = {
            'ids'   : self.ids,
            'model' : 'aikchin.appraisal',
            'from'  : self.read(['employee_id'])[0]
        }
        del self.data_list[:]

        rating_ids = self.env['rating.config'].search([])
        for rating_id in rating_ids:
            rating_description_list = rating_id.rating_descrition.split("\n")
            rating_value = ''
            if self.employee_id.department_id and self.employee_id.department_id.weightage_line_ids:
                for weightage_line in self.employee_id.department_id.weightage_line_ids:
                    if weightage_line.rating_id == rating_id:
                        rating_value = weightage_line.weightage

            data_line = {
                'rating_name'        :rating_id.name,
                'rating_description' : rating_description_list,
                'rating_value'       : rating_value,
            }
            self.data_list.append(data_line)


        return self.env['report'].get_action(self, 'aikchin_modifier_printouts.report_appraisal')

    def cancel(self):
        pass

class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move','partner_ids'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        if data['form'].get('partner_ids'):
            partner_ids =[]
            partner_line_ids = data['form'].get('partner_ids')
            partner_ids = [ x.id for x in self.partner_ids]
            data['form']['partner_ids'] = partner_ids
        return self._print_report(data)

class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.account.report_partnerledger'

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = datetime.strptime(r['date'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            payments = None
            payment_text = ""
            if partner.customer :
                payments = partner.property_payment_term_ids
            elif partner.supplier:
                payments = partner.property_supplier_payment_term_id
            if payments:
                payment_text = ', '.join([payment.name for payment in payments])
            r['payment_term'] = payment_text
            full_account.append(r)
        return full_account

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
                SELECT a.id
                FROM account_account a
                WHERE a.internal_type IN %s
                AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        query = """
                SELECT DISTINCT "account_move_line".partner_id
                FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                WHERE "account_move_line".partner_id IS NOT NULL
                    AND "account_move_line".account_id = account.id
                    AND am.id = "account_move_line".move_id
                    AND am.state IN %s
                    AND "account_move_line".account_id IN %s
                    AND NOT account.deprecated
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()] + data['form'].get('partner_ids')
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref, x.name))

        docargs = {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }
        return self.env['report'].render('account.report_partnerledger', docargs)
