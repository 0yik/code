# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
import datetime


class PosInvoiceReport(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_invoice'

    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        PosOrder = self.env['pos.order']
        ids_to_print = []
        invoiced_posorders_ids = []
        selected_orders = PosOrder.browse(docids)
        for order in selected_orders.filtered(lambda o: o.invoice_id):
            ids_to_print.append(order.invoice_id.id)
            invoiced_posorders_ids.append(order.id)
        not_invoiced_orders_ids = list(set(docids) - set(invoiced_posorders_ids))
        if not_invoiced_orders_ids:
            not_invoiced_posorders = PosOrder.browse(not_invoiced_orders_ids)
            not_invoiced_orders_names = list(map(lambda a: a.name, not_invoiced_posorders))
            raise UserError(_('No link to an invoice for %s.') % ', '.join(not_invoiced_orders_names))

        return Report.sudo().render('modifier_account_invoice_report.custom_report_invoice', {'docs': self.env['account.invoice'].sudo().browse(ids_to_print)})
        
class Invoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def get_date(self,obj,date_type):
        date = ''
        if obj.origin:
            pos_orders = self.env['pos.order'].search([('name','=',str(obj.origin))])
            if any(pos_orders):
                booking = pos_orders[0].booking_id
                if booking:
                    if date_type == 'start_date':
                        date = booking.booking_lines[0].start_date
                    if date_type == 'end_date':
                        date = booking.booking_lines[0].end_date
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%y')
            print "\n\n\n*******final date=",date
        return date
        
    @api.multi
    def get_payment_methods(self,obj):
        if obj.origin:
            pos_orders = self.env['pos.order'].search([('name','=',str(obj.origin))])
            if any(pos_orders):
                return pos_orders[0].payment_journals
