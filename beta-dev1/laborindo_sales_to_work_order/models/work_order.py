# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime




class Worker(models.Model):

    _name = 'worker.worker'

    name = fields.Char('Name')
    email = fields.Char('Email')

class WorkOrder(models.Model):
    _name = 'work.order.so'
    _inherit = 'mail.thread'
    _description = 'Work Order'
    _order = 'id desc'

    name = fields.Char('Name', readonly=True)
    start_date = fields.Date('Scheduled Start Date', required=True)
    end_date = fields.Date('Scheduled End Date', required=True)
    duration = fields.Integer('Duration Until Completion')
    worker_id = fields.Many2one('res.users', 'Worker')
    sale_order_id = fields.Many2one('sale.order', string='Source')
    state = fields.Selection([('draft','Waiting'),('progress','In Progress'),('done','Done'),('cancel','Cancel')], default='draft', string='Status', copy=False)
    note = fields.Text('Note')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('work.order') or 'New'
        return super(WorkOrder, self).create(vals)

    @api.multi
    def button_progress(self):
        template = self.env.ref('laborindo_sales_to_work_order.mail_template_data_work_order1')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

        activity_type_id = self.env['mail.activity.type'].search([('name', '=', 'Work Order')])


        if not activity_type_id:
            activity_type_id = self.env['mail.activity.type'].create(
            {'name': 'Work Order', 'summary': 'Follow up Work Order Entries'})

        model_id = self.env['ir.model'].search([('model', '=', 'work.order.so')])

        activity_vals = {'user_id': self.worker_id.id,
                         'date_deadline': datetime.today(),
                         'activity_type_id': activity_type_id and activity_type_id[0].id,
                         'note': "<p>Follow up Work Order</p>",
                         'res_id': self.id,
                         'res_model': 'work.order.so',
                         'res_model_id': model_id.id,
                         'summary': activity_type_id.summary}

        self.env['mail.activity'].create(activity_vals)

        self.write({'state': 'progress'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_validate(self):
        self.write({'state': 'done'})
        return True

class WorkOrderSO(models.Model):
    _name = "work.order.so"
    _inherit = ['work.order.so', 'mail.activity.mixin']