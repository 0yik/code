# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class WorkOrderLine(models.Model):
    _name = 'work.order.line'

    work_order_id = fields.Many2one('work.order', string='Work Order ID', copy=False)
    name = fields.Char('Work Order', related='work_order_id.name', readonly=True)
    contractor_id = fields.Many2one('res.partner', string='Sub Contractor')
    start_date = fields.Date('Scheduled Start Date', required=True)
    end_date = fields.Date('Scheduled End Date', required=True)
    percentage = fields.Integer('Percentage of Completion (%)', default=10)
    purchase_line_id = fields.Many2one('purchase.order.line', string='PO Line Reference')
    purchase_id = fields.Many2one('purchase.order', related='purchase_line_id.order_id', string='PO Reference')
    state = fields.Selection([('draft', 'Waiting'), ('progress', 'In Progress'), ('done', 'Done')], related='work_order_id.state', string='Status')
    cost = fields.Float('Cost')

    @api.onchange('percentage')
    def onchange_percentage(self):
        warning = {}
        if self.percentage <= 0:
            self.percentage = 10.0
            warning = {'title': 'Value Error!', 'message': 'Percentage value can not be less than or equal to 0.'}
        elif self.percentage > 100:
            self.percentage = 10.0
            warning = {'title': 'Value Error!', 'message': 'Percentage value can not be greater than or equal to 100.'}
        return {'warning': warning}

WorkOrderLine()

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_line_ids.ids)

    @api.depends('work_order_line_ids', 'work_order_line_ids.start_date', 'work_order_line_ids.end_date')
    def compute_schedule_date(self):
        for record in self:
            start_dates, end_dates = [], []
            for line in record.work_order_line_ids:
                start_date = datetime.strptime(line.start_date, DF)
                start_dates.append(start_date)
                end_date = datetime.strptime(line.end_date, DF)
                end_dates.append(end_date)
            record.schedule_start_date = start_dates and min(start_dates)
            record.schedule_end_date = end_dates and max(end_dates)

    work_order_line_ids = fields.One2many('work.order.line', 'purchase_line_id', 'Work Orders', copy=True)
    product_type = fields.Selection(related="product_id.type", string='Product Type')
    description = fields.Text('Description')
    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')
    schedule_start_date = fields.Date(compute='compute_schedule_date', string='Scheduled Start Date')
    schedule_end_date = fields.Date(compute='compute_schedule_date', string='Scheduled End Date')

    @api.model
    def create(self, vals):
        record = super(PurchaseOrderLine, self).create(vals)
        record.validate_work_order_line()
        return record

    @api.multi
    def write(self, vals):
        result = super(PurchaseOrderLine, self).write(vals)
        self.validate_work_order_line()
        return result

    @api.multi
    def validate_work_order_line(self):
        for record in self:
            if record.product_type and record.product_type == 'service':
                # Validating the work order percentage
                if record.work_order_line_ids:
                    value = 0
                    check_100 = False
                    total_cost = 0.0
                    for line in record.work_order_line_ids:
                        if value >= line.percentage:
                            raise UserError('Work order percentage [%s] for <%s> is less than or equal to the previous line percentage [%s]' % (line.percentage, record.product_id.name, value))
                        if line.percentage == 100:
                            check_100 = True
                        value = line.percentage
                        total_cost += line.cost
                    if not check_100:
                        raise UserError('There must be 100 percentage in work order line for product <%s>' % record.product_id.name)
                    if total_cost != (record.price_unit * record.product_qty):
                        raise UserError('Sum of work order line cost (%s) is not equal to the price (%s) of the product <%s>' % (total_cost, record.price_unit * record.product_qty, record.product_id.name))
        return True

    # @api.multi
    # def validate_work_order_line(self):
    #     for record in self:
    #         # Validating the work order percentage
    #         value = 0
    #         check_100 = False
    #         total_cost = 0.0
    #         for line in record.work_order_line_ids:
    #             if value >= line.percentage:
    #                 raise UserError('Work order percentage [%s] for <%s> is less than or equal to the previous line percentage [%s]' % (line.percentage, record.product_id.name, value))
    #             if line.percentage == 100:
    #                 check_100 = True
    #             value = line.percentage
    #             total_cost += line.cost
    #         if not check_100:
    #             raise UserError('There must be 100 percentage in work order line for product <%s>' % record.product_id.name)
    #         if total_cost != (record.price_unit * record.product_qty):
    #             raise UserError('Sum of work order line cost (%s) is not equal to the price (%s) of the product <%s>' % (total_cost, record.price_unit * record.product_qty, record.product_id.name))
    #     return True


PurchaseOrderLine()

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.invoice_lines.invoice_id.state', 'order_line.work_order_line_ids.work_order_id.invoice_count')
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id')
            for line1 in order.order_line:
                for line2 in line1.work_order_line_ids:
                    invoices += line2.work_order_id.invoice_ids
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    @api.multi
    def compute_work_order_count(self):
        for record in self:
            work_order_count = 0
            for line in record.order_line:
                work_order_count += len([1 for line2 in line.work_order_line_ids if line2.work_order_id])
            record.work_order_count = work_order_count

    invoice_count = fields.Integer(compute="_compute_invoice", string='# of Bills', copy=False, default=0)
    invoice_ids = fields.Many2many('account.invoice', compute="_compute_invoice", string='Bills', copy=False)
    work_order_count = fields.Integer(compute='compute_work_order_count', string='Work Order Count')

    @api.multi
    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        # Create work orders
        for record in self:
            for purchase_line in record.order_line:
                work_order_line_ids = purchase_line.work_order_line_ids.ids[::-1]
                work_order_lines = self.env['work.order.line'].browse(work_order_line_ids)
                for work_line in work_order_lines:
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

    @api.multi
    @api.depends('name', 'partner_ref')
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result

    @api.onchange('order_line')
    @api.depends('order_line.work_order_line_ids')
    def onchange_order_line(self):
        for record in self.order_line:
            if record.product_type and record.product_type == 'service':
                # Validating the work order percentage
                if record.work_order_line_ids:
                    value = 0
                    check_100 = False
                    total_cost = 0.0
                    for line in record.work_order_line_ids:
                        if value >= line.percentage:
                            raise UserError('Work order percentage [%s] for <%s> is less than or equal to the previous line percentage [%s]' % (line.percentage, record.product_id.name, value))
                        if line.percentage == 100:
                            check_100 = True
                        value = line.percentage
                        total_cost += line.cost
                    if not check_100:
                        raise UserError('There must be 100 percentage in work order line for product <%s>' % record.product_id.name)
                    if total_cost != (record.price_unit * record.product_qty):
                        raise UserError('Sum of work order line cost (%s) is not equal to the price (%s) of the product <%s>' % (total_cost, record.price_unit * record.product_qty, record.product_id.name))

    # def onchange_order_line(self):
    #     for record in self.order_line:
    #         # Validating the work order percentage
    #         value = 0
    #         check_100 = False
    #         total_cost = 0.0
    #         for line in record.work_order_line_ids:
    #             if value >= line.percentage:
    #                 raise UserError('Work order percentage [%s] for <%s> is less than or equal to the previous line percentage [%s]' % (line.percentage, record.product_id.name, value))
    #             if line.percentage == 100:
    #                 check_100 = True
    #             value = line.percentage
    #             total_cost += line.cost
    #         if not check_100:
    #             raise UserError('There must be 100 percentage in work order line for product <%s>' % record.product_id.name)
    #         if total_cost != (record.price_unit * record.product_qty):
    #             raise UserError('Sum of work order line cost (%s) is not equal to the price (%s) of the product <%s>' % (total_cost, record.price_unit * record.product_qty, record.product_id.name))
    #
PurchaseOrder()