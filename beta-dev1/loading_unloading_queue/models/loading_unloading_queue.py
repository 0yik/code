from odoo import models, fields, api, _
from datetime import datetime


class LoadingQueue(models.Model):
    _name = 'loading.queue'
    _rec_name = 'queue_number'

    @api.multi
    @api.onchange('reference')
    def onchange_lines(self):
        stock_pack_operation_obj = self.reference.pack_operation_product_ids
        res_list = []
        for res in stock_pack_operation_obj:
            res_list.append((0, 0, {'product_id': res.product_id.name, 'product_qty': res.product_qty}))
        self.pack_operation_product_ids = res_list

    queue_number = fields.Many2one('generate.queue', 'Queue Number')
    check = fields.Boolean(string="check", default=False)
    queue_no = fields.Char(related='queue_number.queue_number', readonly=True)
    created_date = fields.Datetime(related='queue_number.created_date', string='Date Created', readonly=True)
    reference = fields.Many2one(related='queue_number.reference', string='Reference', readonly=True)
    vehicle_type = fields.Char('Vehicle Type', required=True)
    vehicle_model = fields.Char('Vehicle Model', required=True)
    vehicle_license = fields.Char('Vehicle License Plate', required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In progress'),
                              ('finished', 'Finished')], default='draft', String='Status')
    start_time = fields.Datetime('Time start', readonly=True)
    end_time = fields.Datetime('Time end', readonly=True)
    duration = fields.Char('Duration', readonly=True)
    source_doc = fields.Many2one('sale.order', 'Source Document')
    pack_operation_product_ids = fields.One2many('loading.queue.lines', 'queue_line_id', string='Product')

    @api.multi
    def time_start(self, vals):
        if not self.start_time:
            self.start_time = datetime.now()
            self.check = True
            vals.update({'state': 'in_progress'})
            return self.write(vals)

    @api.multi
    def time_end(self, values):
        if not self.end_time and self.start_time:
            self.check = False
            self.end_time = datetime.now()
            values.update({'state': 'finished'})

            start_time = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')

            duration = end_time - start_time
            values.update({'duration': duration})
            return self.write(values)


class LoadingQueueLines(models.Model):
    _name = "loading.queue.lines"

    queue_line_id = fields.Many2one('loading.queue')
    product_id = fields.Char('Product')
    product_qty = fields.Char('Qty')
