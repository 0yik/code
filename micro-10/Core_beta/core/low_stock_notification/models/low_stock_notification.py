# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class low_stock_notification(models.Model):
    _name = 'low.stock.notification'

    @api.model
    def _default_date_run(self):
        now = datetime.now()
        if now.hour >= 22:
            now = now + timedelta(days=1)
            return datetime.strptime(now.strftime('%Y-%m-%d 22:00:00'), '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.strptime(now.strftime('%Y-%m-%d 22:00:00'), '%Y-%m-%d %H:%M:%S')

    name = fields.Char('Name')
    location_id = fields.Many2one('stock.location', string='Location', required=True)
    line_ids = fields.One2many('low.stock.notification.line', 'parent_id', string="Products")
    recipient_ids = fields.Many2many('res.users', relation='low_stock_notification_res_user_rel',
                                     column1='low_stock_notification_id', column2='user_id', string='Email To',
                                     required=True)
    template_id = fields.Many2one('mail.template', 'Template', required=True)
    next_run_date = fields.Datetime('Next Run', required=True, default=_default_date_run)

    @api.model
    def run_cron_notification(self):
        model_ids = self.search([])
        for record in model_ids:
            now = datetime.now()
            time_notify = datetime.strptime(record.next_run_date, '%Y-%m-%d %H:%M:%S')
            if now < time_notify:
                continue
            record.next_run_date = time_notify + timedelta(days=1)
            record._cron_notification()
        return True

    @api.model
    def _cron_notification(self):
        excel_obj = self.env['low.stock.export.excel']
        data = []
        data = self.compute_to_notification_normal()
        if data != []:
            attachment = excel_obj.make_file(data, self.location_id.complete_name)
            self._send_mail_via_template(attachment)
        return True

    @api.model
    def compute_to_notification_normal(self):
        quant_obj = self.env['stock.quant']
        quant_ids = quant_obj.search([('location_id', '=', self.location_id.id)])
        data = []
        for line in self.line_ids:
            quant_product = quant_ids.filtered(lambda r: r.product_id.id == line.product_id.id)
            avaiable_qty = sum(x.qty for x in quant_product)
            if line.quantity >= avaiable_qty:
                data.append((line.product_id.name, avaiable_qty))
        return data

    @api.model
    def _send_mail_via_template(self, attachment):
        if self.recipient_ids and len(self.recipient_ids) > 0 and self.template_id and self.template_id.id:
            email_to = ','.join(self.recipient_ids.mapped('partner_id.email'))
            if email_to:
                self.template_id.write({
                    'email_to': email_to,
                    'attachment_ids': [(6, 0, [attachment.id])]
                })
                result = self.template_id.send_mail(self.id, True)
                return result


class low_stock_notification_line(models.Model):
    _name = 'low.stock.notification.line'

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string="Products", required=True)
    quantity = fields.Float('Quantity', required=True)
    parent_id = fields.Many2one('low.stock.notification', 'Parent ID')