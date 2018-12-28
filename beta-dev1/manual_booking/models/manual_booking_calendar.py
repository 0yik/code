from odoo import api, models, fields

class manual_booking_calendar(models.Model):
    _inherit = 'calendar.event'

    contract_id = fields.Many2one('account.analytic.account', string="Contract")
    sales_order_id = fields.Many2one('sale.order',string="Sales Order")
    team_id = fields.Many2one('crm.team',string="Team")
    customer_id = fields.Many2one('res.partner',string="Customer")
    job_details = fields.Text(string="Job Details")
    time_in = fields.Float(string="Time in")
    time_out = fields.Float(string="time out")

    @api.onchange('contract_id','sales_order_id')
    def onchane_customer(self):
        if self.contract_id:
            self.customer_id = self.contract_id.partner_id
        if self.sales_order_id:
            self.customer_id = self.sales_order_id.partner_id