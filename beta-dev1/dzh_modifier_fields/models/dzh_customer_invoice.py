# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class account_invoice(models.Model):
    _inherit = 'account.invoice'

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
            end_day = start.day
            while True:
                end_format = '%s-%s-%s' % (end_year, end_month, end_day)
                try:
                    record.x_end_date = datetime.strptime(end_format, '%Y-%m-%d')
                    break
                except:
                    end_day -= 1

            # for n in range(1,month+1):
            #     start = datetime.strptime(self.x_subscription_period, '%Y-%m-%d')
            #     add_month = n % 12
            #     add_years = int(n / 12) + (int(start.month) + add_month) / 12
            #     end_month = (int(start.month) + add_month) % 12 if (int(start.month) + add_month) / 12 > 0  else int(
            #         start.month) + add_month
            #     end_year = start.year + add_years
            #     end_day = start.day
            #
            #     end_format1 = '%s-%s-%s' % (end_year, end_month, end_day)
            #     self.monthly_revenue_ids += self.monthly_revenue_ids.new({
            #             'date': end_format1,
            #         })

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            sales_team_ids = self.env['crm.team'].search([])
            for sales_team in sales_team_ids:
                fla = 0
                for user in sales_team.member_ids:
                    if user.id == self.user_id.id:
                        fla = 1
                if fla == 1:
                    self.team_id = sales_team.id
                    break
                else:
                    self.team_id = None

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.user_id and self.team_id:
            fla = 0
            for user in self.team_id.member_ids:
                if user.id == self.user_id.id:
                    fla = 1
            if fla == 0:
                self.user_id = None

    @api.onchange('x_month_number', 'x_subscription_period', 'invoice_line_ids')
    def update_monthly_revenue(self):
        for record in self:
            month = record.x_month_number
            start = datetime.strptime(record.x_subscription_period, '%Y-%m-%d')
            monthly_revenue_ids = record.monthly_revenue_ids.browse([])
            for n in range(0, month):
                end_format = self.get_date(n, start)
                terminal_amount = 0
                data_amount = 0
                count = 1
                if record.invoice_line_ids:
                    count = len(record.invoice_line_ids)
                for line in record.invoice_line_ids:
                    line.quantity = record.x_month_number
                    if line.product_id.terminal_ok == True:
                        terminal_amount += line.price_unit
                    else:
                        data_amount += line.price_unit
                monthly_revenue_ids += record.monthly_revenue_ids.new({
                    'date': end_format,
                    'terminal_amount': terminal_amount,
                    'data_amount': data_amount,
                    'total_amount': (terminal_amount + data_amount),
                    'count_line_invoice' : count,
                })
            record.monthly_revenue_ids = monthly_revenue_ids

    def get_date(self, month, start):
        end_format = start + relativedelta(months=month)
        if end_format:
            end_format = end_format.strftime('%Y-%m-%d')
        return end_format

    @api.onchange('partner_id')
    def onchange_partner_id_sale_order(self):
        if self.partner_id and self.partner_id.id:
            if self.invoice_line_ids and len(self.invoice_line_ids) > 0:
                self.invoice_line_ids.write({'partner_from_io': self.partner_id.id})
        return

    x_subscription_period = fields.Date('Subscription Period', default=fields.Datetime.now)
    x_end_date = fields.Date("End Date", compute=compute_end_date)
    x_contact_term = fields.Text('Contract Term')
    x_month_number = fields.Integer('Number of Month', default=0)
    cr_number = fields.Text('CR Number')
    user_send_mail = fields.Char(default="")
    monthly_revenue_ids = fields.One2many('monthly.revenue.line', 'account_invoice_id')
    terminal_date = fields.Date(string="Termination Date")

    @api.model
    def send_mail_notification(self):
        day_after = (datetime.now()+timedelta(days = 30)).strftime('%Y-%m-%d')
        day_after = datetime.strptime(day_after,'%Y-%m-%d')
        invoice_ids = self.env['account.invoice'].search([])
        invoice = []
        for invoice_id in invoice_ids:
            invoice_id.compute_end_date()
            if invoice_id.x_end_date:
                x_end_day = datetime.strptime(invoice_id.x_end_date,'%Y-%m-%d')
                if  x_end_day == day_after:
                    invoice.append(invoice_id.id)
        invoice_need_send_mail = self.env['account.invoice'].search([('id','in',invoice)])
        if invoice_need_send_mail:
            for invoice_send_mail in invoice_need_send_mail:
                self.send_mail(invoice_send_mail.user_id,invoice_send_mail)
                user_ids = self.env['res.users'].search([])
                for user_id in user_ids:
                    if user_id.re_notification or user_id.support_email:
                        self.send_mail(user_id, invoice_send_mail)

    def send_mail(self,user_id,invoice):
        email_from = invoice.company_id.email or 'Administrator <admin@example.com>'
        email_to = user_id.email
        subject = 'Subscription End Date of Invoices'
        # message = """
        #     <html>
        #         <body>
        #             <p>Dear %s,<br><br>
        #                 This invoice is approaching Subscription End Date in 1 month.<br>
        #                 Invoice : %s<br>
        #                 Sales Person : %s<br>
        #                 Subscription End Date : %s<br><br>
        #
        #                 Regards,<br>
        #                 DZH International
        #              </p>
        #         </body>
        #     </html>""" % (user_id.name,invoice.number,invoice.user_id.name,invoice.x_end_date)

        message = """
        <html>
            <body>
				<div style="font-family: 'Lucida Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
					<p style="margin-left: 40px;">Dear %s,</p>

					<p style="border-left: 1px solid #8e0000; margin-left: 30px;">
					    <span style="margin-left: -130px;">
                           <strong>This invoice is approaching Subscription End Date in 1 month.</strong><br/>
                           Invoice: <strong>%s</strong><br/>
                           Sales Person: <strong>%s</strong><br/>
                           Subscription End Date: <strong>%s</strong><br/>
					    </span>
					</p>
					<br/>
					<span style="margin-left: -80px;">Regards,</span><br/>
					<span style="margin-left: -80px;"><strong>DZH International</strong></span>
				</div>
		    </body>
		<html>"""% (user_id.name,invoice.number,invoice.user_id.name,invoice.x_end_date)

        vals = {
            'state': 'outgoing',
            'subject': subject,
            'body_html': '<pre>%s</pre>' % message,
            'email_to': email_to,
            'email_from': email_from,
        }
        if vals:
            email_exist = False
            if invoice.user_send_mail:
                user_send_mails = invoice.user_send_mail.split('-')
                for user_send_mail in user_send_mails:
                    if int(user_send_mail) == user_id.id:
                        email_exist = True
            if not email_exist:
                email_id = self.env['mail.mail'].create(vals)
                if email_id:
                    email_id.send()
                    if invoice.user_send_mail:
                        user_send_mail = invoice.user_send_mail + '-' + str(user_id.id)
                    else:
                        user_send_mail = str(user_id.id)
                    invoice.write({'user_send_mail':user_send_mail})
    def onchane_status(self):
        invoice_ids = self.env['account.invoice'].search([])
        fla = 0
        for invoice_id in invoice_ids:
            if not invoice_id.monthly_revenue_ids:
                invoice_id.update_monthly_revenue()
                fla += 1
            if fla == 50:
                break

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    account_user_id = fields.Many2many("dzh.partner.user",id1='invoice_line_id', id2='account_user_id', string="User ID")
    subscription_period = fields.Date('Subscription Period')
    start_date = fields.Datetime("Start Date" , default=fields.Datetime.now)
    end_date = fields.Datetime("End Date" , default=fields.Datetime.now)
    partner_from_io = fields.Many2one('res.partner', string='Partner ID')
    number_user_id = fields.Integer(string='User ID')

    @api.onchange('account_user_id')
    def number_user_id_depends(self):
        if self.account_user_id:
            self.number_user_id = len(self.account_user_id)

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceLine, self).default_get(fields)
        if self._context.get('quantity', False):
            res['quantity'] = self._context.get('quantity', False)
        if self._context.get('invoice_order_partner_id', False):
            res['partner_from_io'] = self._context.get('invoice_order_partner_id', False)
        return res

    # @api.model
    # def create(self,vals):
    #     res = super(AccountInvoiceLine, self).create(vals)
    #     if res.account_user_id:
    #         res.number_user_id = len(res.account_user_id)
    #     return res
    #
    # @api.multi
    # def write(self,vals):
    #     if 'account_user_id' in vals:
    #         a = vals['account_user_id']
    #     res = super(AccountInvoiceLine, self).write(vals)
    #     return res



class monthly_revenue(models.Model):
    _name = 'monthly.revenue.line'

    account_invoice_id = fields.Many2one('account.invoice')
    date = fields.Date('Date')
    terminal_amount = fields.Float('Terminal Amount')
    data_amount  = fields.Float('Data Amount')
    total_amount = fields.Float("Total Amount")
    count_line_invoice = fields.Integer()


# class account_analytic(models.Model):
#     _inherit = 'account.invoice.report'
#
#     terminal = fields.Many2one('monthly.revenue.line', string="Terminal", readonly=True)
#     data = fields.Many2one('monthly.revenue.line', string="Data", readonly=True)
#     monthly_revenue = fields.Float("Monthly Revenue", readonly=True)

