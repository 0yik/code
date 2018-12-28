# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta, date


class low_stock_notification_runrate(models.Model):
    _inherit = 'low.stock.notification'

    type = fields.Selection([('normal', 'Normal'), ('runrate', ('Run Rate'))], string='Type', default='normal')
    rr_line_ids = fields.One2many('low.stock.notification.line.rr', 'rr_parent_id', string='RR Line Ids')

    @api.model
    def _cron_notification(self):
        if self.type == 'normal':
            return super(low_stock_notification_runrate, self)._cron_notification()
        elif self.type == 'runrate':
            excel_obj = self.env['low.stock.export.excel']
            data = []
            data = self.compute_to_notification_runrate()
            if data != []:
                attachment = excel_obj.make_file_runrate(data)
                self._send_mail_via_template(attachment, self.location_id.complete_name)
            return True

    @api.model
    def compute_to_notification_runrate(self):
        quant_obj = self.env['stock.quant']
        quant_ids = quant_obj.search([('location_id', '=', self.location_id.id)])
        data = []
        for line in self.rr_line_ids:
            quant_product = quant_ids.filtered(lambda r: r.product_id.id == line.rr_product_id.id)
            avaiable_qty = sum(x.qty for x in quant_product)

            now = date.today()
            sample_date = now - timedelta(days=line.rr_sample_date)
            out_move = quant_ids.history_ids.filtered(lambda r: datetime.strptime(r.date,
                                                                                  '%Y-%m-%d %H:%M:%S') >= sample_date and r.location_id == self.location_id.id and r.location_dest_id != self.location_id.id)
            out_qty = sum(x.product_uom_qty for x in out_move)
            if out_qty != 0:
                rr_index = out_qty / line.rr_sample_date
                if (avaiable_qty / rr_index) <= line.rr_check_notify_date:
                    data.append((line.rr_product_id.name, rr_index, line.rr_product_id.qty_available))
        return data


class low_stock_notification_line_runrate(models.Model):
    _name = 'low.stock.notification.line.rr'

    name = fields.Char('Name')
    rr_product_id = fields.Many2one('product.product', string="Products", required=True)
    rr_sample_date = fields.Integer('Sample Data (No of Days)', required=True, default=1)
    rr_check_notify_date = fields.Integer('No of Days before out of stock', required=True, default=1)
    rr_parent_id = fields.Many2one('low.stock.notification', string='Parent ID')
