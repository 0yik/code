from odoo import models, fields, api
from datetime import datetime, timedelta

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.depends('annual_revenue','planned_revenue')
    @api.onchange('planned_revenue')
    def _annual_revenue_calculate(self):
        if self.planned_revenue:
            self.annual_revenue = self.planned_revenue * 12
        if self.planned_revenue ==0:
            self.annual_revenue = 0
        return

    @api.depends('annual_revenue','planned_revenue')
    @api.onchange('annual_revenue')
    def _mothy_revenue_calculate(self):
        if self.annual_revenue:
            self.planned_revenue = 1.000*self.annual_revenue/12
        if self.annual_revenue ==0:
            self.planned_revenue = 0
        return

    @api.one
    @api.depends('x_subscription_period', 'x_month_number')
    def compute_end_date(self):
        for record in self:
            if not record.x_subscription_period:
                return
            month = record.x_month_number or 0
            start = datetime.strptime(record.x_subscription_period, '%Y-%m-%d')
            add_month = month % 12
            add_years = int(month / 12) + (int(start.month) + add_month) / 12
            end_month = (int(start.month) + add_month) % 12 if (int(start.month) + add_month) / 12 > 0  else int(
                start.month) + add_month
            end_year = start.year + add_years
            end_day = start.day -1
            if end_day == 0:
                end_month = end_month -1
                end_day = 31
                if end_month == 0:
                    end_month=12
                    end_year = end_year - 1

            while True:
                end_format = '%s-%s-%s' % (end_year, end_month, end_day)
                try:
                    record.x_end_date = datetime.strptime(end_format, '%Y-%m-%d')
                    break
                except:
                    end_day -= 1

    x_subscription_period = fields.Date(string="Subscription Period", default=fields.Datetime.now)
    one_time_revenue = fields.Integer('One Time Revenue')
    annual_revenue = fields.Float('Annual Revenue')
    x_month_number = fields.Integer('Number of Month', default=0)
    x_end_date = fields.Date("End Date", compute=compute_end_date)
    invoice_type = fields.Selection([('fiancial', 'Financial Terminal'),('trading_gts', 'Trading (GTS)'), ('trading_dzh', 'Trading (DZHI)'), ('event','Conference & Event'),('digital','Digital')])




