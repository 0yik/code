# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def amount_to_text(self, amount_total, currency='IDR'):
    	word =  num2words(amount_total, lang='id')
    	return word.upper()

class report_invoice_signature(models.TransientModel):
    _name = 'report.invoice.signature'

    signature = fields.Selection([(1,'Diah Ayu Wulandari'),(2,'Lenny Liliane Gan')],default=1,string='Signature')

    @api.multi
    def print_invoice(self):
        if self._context.get('active_ids',False) and self._context.get('active_model',False) == 'account.invoice':
            # data = {
            #     'ids': self._context.get('active_ids',False),
            #     'model': 'account.invoice',
            # }

            # return {
            #     'type'          : 'ir.actions.report.xml',
            #     'report_name'   : 'laborindo_report_invoice_soc.report_invoice2',
            #     'datas'         : data
            data = {}
            data['ids'] = self._context.get('active_ids',False)
            data['model'] = 'account.invoice'
            if self.signature:
                data.update({'signature': 'Diah Ayu Wulandari' if self.signature == 1 else 'Lenny Liliane Gan'})
            act = self.env['report'].get_action(self, 'laborindo_report_invoice_soc.report_invoice2',data=data)
            return act
        # }
report_invoice_signature()

class Render_Print_Invoice(models.AbstractModel):
    _name = 'report.laborindo_report_invoice_soc.report_invoice2'

    @api.multi
    def render_html(self, docids, data=None):
        docargs = {
            'doc_ids': data.get('ids',False),
            'doc_model': 'account.invoice',
            'docs': self.env['account.invoice'].browse(data.get('ids',False)),
            'data': data,
            'signature': data.get('signature',''),
            'po_number_reference': '',

        }
        sale_id = self.env['sale.order'].search([('name','=',self.env['account.invoice'].browse(data.get('ids',False)).name)],limit=1)
        if sale_id:
            docargs.update({'po_number_reference':sale_id.po_number_reference or ''})
        return self.env['report'].render('laborindo_report_invoice_soc.report_invoice2', docargs)

Render_Print_Invoice()