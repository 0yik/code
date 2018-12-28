from odoo import models, fields, api
from datetime import datetime

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    probability = fields.Float('Probability (%)',
                               help="This percentage depicts the default/average probability of the Case for this stage to be a success")


    invoice_type = fields.Selection([('fiancial', 'Financial Terminal'),('trading_gts', 'Trading (GTS)'), ('trading_dzh', 'Trading (DZHI)'), ('event','Conference & Event'),('digital','Digital')])

    invoice_arrange = fields.Selection([('new','New'),('renewal','Renewal'),('fallout','FallOut/Cancellation'),('incID', 'Increase of ID'),('incDT', 'Increase of Data/Pricing'), ('decID', 'Decrease of ID'),('decDT','Decrease of Data/Pricing'),('other','Others')])

    other_descripton = fields.Text()

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
            end_day = start.day - 1
            if end_day == 0:
                if end_month == 0:
                    end_day = 31
                    end_month = 12
                    end_year -= 1
                else:
                    end_month = end_month - 1
                    end_day = 31
                    if end_month == 0:
                        end_month = 12
                        end_year = end_year - 1

            else:
                if end_month == 0:
                    end_month = 12
                    end_year = end_year - 1
            while True:
                end_format = '%s-%s-%s' % (end_year, end_month, end_day)
                try:
                    record.x_end_date = datetime.strptime(end_format, '%Y-%m-%d')
                    break
                except:
                    end_day -= 1

    x_subscription_period = fields.Date(string="Subscription Period", default=fields.Datetime.now)
    annual_revenue = fields.Float('Annual Revenue')
    x_month_number = fields.Integer('Number of Month', default=0)
    x_end_date = fields.Date("End Date", compute=compute_end_date)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('x_subscription_period', 'x_month_number')
    def compute_end_date(self):
        if not self.x_subscription_period:
            return
        month = self.x_month_number or 0
        start = datetime.strptime(self.x_subscription_period, '%Y-%m-%d')
        add_month = month % 12
        add_years = int(month / 12) + (int(start.month) + add_month) / 12
        end_month = (int(start.month) + add_month) % 12 if (int(start.month) + add_month) / 12 > 0  else int(
            start.month) + add_month
        end_year = start.year + add_years
        end_day = start.day - 1
        if end_day == 0:
            if end_month == 0:
                end_day = 31
                end_month = 12
                end_year -= 1
            else:
                end_month = end_month - 1
                end_day = 31
                if end_month == 0:
                    end_month = 12
                    end_year = end_year - 1
        else:
            if end_month == 0:
                end_month = 12
                end_year = end_year - 1

        while True:
            end_format = '%s-%s-%s' % (end_year, end_month, end_day)
            try:
                self.x_end_date = datetime.strptime(end_format, '%Y-%m-%d')
                break
            except:
                end_day -= 1


    x_subscription_period = fields.Date('Subscription Period', default=fields.Datetime.now)
    x_end_date = fields.Date("End Date", compute=compute_end_date)
    x_contact_term = fields.Text('Contract Term')
    x_month_number = fields.Integer('Number of Month', default=0)

    @api.onchange('partner_id')
    def onchange_partner_id_sale_order(self):
        if self.partner_id and self.partner_id.id:
            if self.order_line and len(self.order_line) > 0:
                self.order_line.write({'partner_from_so': self.partner_id.id})
        return
