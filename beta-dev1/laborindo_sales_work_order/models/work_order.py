# coding=utf-8
from odoo import api, fields, models
from datetime import datetime

class WorkOrder(models.Model):
    _name = 'work.order'
    _inherit = 'mail.thread'
    _description = 'Work Order'
    _order = 'id desc'

    # @api.multi
    # def compute_invoice_count(self):
    #     for record in self:
    #         record.invoice_count = len(record.invoice_ids.ids)

    name = fields.Char('Name', readonly=True)
    product_id = fields.Many2one('product.product', required=True, string='Product')
    contractor_id = fields.Many2one('res.partner', required=True, string='Sub Contractor')
    partner_id = fields.Many2one('res.partner', required=True, string='Customer')
    start_date = fields.Date('Scheduled Start Date', required=True)
    end_date = fields.Date('Scheduled End Date', required=True)
    percentage = fields.Integer('Percentage of Completion (%)')
    duration = fields.Integer('Duration Until Completion')
    sale_order_id = fields.Many2one('sale.order', related='sale_order_line_id.order_id', store=True, string='SO Reference')
    sale_order_line_id = fields.Many2one('sale.order.line', string='SO Line Reference')
    currency_id = fields.Many2one('res.currency', related='sale_order_line_id.currency_id', string='Currency')
    state = fields.Selection([('draft','Waiting'),('progress','In Progress'),('done','Done'),('cancel','Cancel')], default='draft', string='Status')
    cost = fields.Float('Cost')
    # invoice_ids = fields.Many2many('account.invoice', string='Invoices')
    # invoice_count = fields.Integer(compute='compute_invoice_count', string='Invoice Count')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('work.order') or 'New'
        return super(WorkOrder, self).create(vals)

    @api.multi
    def button_progress(self):
        self.write({'state': 'progress'})
        return True

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    # @api.multi
    # def button_validate(self):
    #     vals = {}
    #     line_vals = {}
    #     journal_id = self.env['account.invoice']._default_journal()
    #     vals['partner_id'] = self.partner_id.id
    #     vals['date_invoice'] = datetime.now().date()
    #     vals['account_id'] = self.partner_id.property_account_receivable_id.id
    #     vals['name'] = self.name
    #     vals['currency_id'] = self.currency_id.id
    #     vals['type'] = 'out_invoice'
    #     vals['journal_id'] = journal_id.id
    #     line_vals['product_id'] = self.product_id.id
    #     line_vals['name'] = self.product_id.name
    #     line_vals['account_id'] = journal_id.default_credit_account_id.id
    #     line_vals['quantity'] = 1
    #     line_vals['price_unit'] = self.cost
    #     vals['invoice_line_ids'] = [(0,0,line_vals)]
    #     invoice_id = self.env['account.invoice'].create(vals)
    #     self.write({'state': 'done', 'invoice_ids': [(4, invoice_id.id)]})
    #     return True

    # @api.multi
    # def action_view_invoice(self):
    #     action = self.env.ref('account.action_invoice_tree').read()[0]
    #     action['domain'] = [('id', 'in', self.invoice_ids.ids)]
    #     return action

WorkOrder()