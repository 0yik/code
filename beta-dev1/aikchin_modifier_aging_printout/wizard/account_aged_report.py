# -*- coding: utf-8 -*-


import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ReportAgedPartnerBalance(models.AbstractModel):

    _inherit = 'report.account.report_agedpartnerbalance'

    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))

        if data['form']['result_selection'] == 'customer':
            account_type = ['receivable']
        elif data['form']['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']

        movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move, data['form']['period_length'])
        # Filtering account.move.line of selected partners
        if data['form'].get('partner_ids'):
            movelines = [line for line in movelines if line['partner_id'] in data['form'].get('partner_ids')]
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
            vals={
                'credit_limit' : credit_limit and credit_limit or '',
                'payment': payment and payment or '',
                'sale': sale and sale or '',
                'p_id': p_id and p_id or '',
                'phone' : phone and phone or ''
            }
            movelines[count].update(vals)
            count = count + 1
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
        }
        return self.env['report'].render('account.report_agedpartnerbalance', docargs)