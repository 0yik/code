# -*- coding: utf-8 -*-
from odoo import api, fields, models

class WorkOrderLine(models.Model):
    _name = 'work.order.line'

    work_order_id = fields.Many2one('work.order', string='Work Order ID', copy=False)
    name = fields.Char('Work Order', related='work_order_id.name', readonly=True)
    contractor_id = fields.Many2one('res.partner', string='Sub Contractor')
    start_date = fields.Date('Scheduled Start Date', required=True)
    end_date = fields.Date('Scheduled End Date', required=True)
    percentage = fields.Integer('Percentage of Completion (%)')
    purchase_line_id = fields.Many2one('purchase.order.line', string='PO Line Reference')
    purchase_id = fields.Many2one('purchase.order', related='purchase_line_id.order_id', string='PO Reference')
    state = fields.Selection([('draft', 'Waiting'), ('progress', 'In Progress'), ('done', 'Done')], related='work_order_id.state', string='Status')
    cost = fields.Float('Cost')

WorkOrderLine()

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_line_ids.ids)

    work_order_line_ids = fields.One2many('work.order.line', 'purchase_line_id', 'Work Orders')
    product_type = fields.Selection(related="product_id.type", string='Product Type')
    description = fields.Text('Description')
    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')

PurchaseOrderLine()

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def compute_work_order_count(self):
        for record in self:
            work_order_count = 0
            for line in record.order_line:
                work_order_count += len([1 for line2 in line.work_order_line_ids if line2.work_order_id])
            record.work_order_count = work_order_count

    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')

    @api.multi
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        # Create work orders
        for record in self:
            for purchase_line in record.order_line:
                for work_line in purchase_line.work_order_line_ids:
                    vals = {}
                    vals['product_id'] = purchase_line.product_id.id
                    vals['contractor_id'] = work_line.contractor_id.id
                    vals['partner_id'] = purchase_line.partner_id.id
                    vals['start_date'] = work_line.start_date
                    vals['end_date'] = work_line.end_date
                    vals['percentage'] = work_line.percentage
                    vals['cost'] = work_line.cost
                    vals['purchase_id'] = work_line.purchase_id.id
                    vals['purchase_line_id'] = work_line.purchase_line_id.id
                    vals['currency_id'] = work_line.purchase_id.currency_id.id
                    work_order_id = self.env['work.order'].create(vals)
                    work_line.work_order_id = work_order_id.id
        return True

    @api.multi
    def action_view_workorder(self):
        action = self.env.ref('internal_purchase_milestones.action_work_order').read()[0]
        action['domain'] = [('purchase_id', 'in', self.ids)]
        return action

PurchaseOrder()