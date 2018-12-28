# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To be Approved'),
        ('purchase', 'Purchase Order'),
        ('reject','Rejected'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    is_vendor_bill = fields.Boolean('Vendor Bill')
    is_unreceived = fields.Boolean('Unreceived')

    @api.depends('approval_id','approval_id.user_id')
    def _compute_approve_check(self):
        for record in self:
            if record.approval_id.user_id:
                if record.approval_id.user_id.id == self.env.user.id:
                    record.approve_check = True

    approval_id = fields.Many2one('hr.employee', string='Approval')
    approve_check = fields.Boolean(compute='_compute_approve_check', string='Approve Check')

    @api.multi
    def send_email(self):
        mail_vals = {}
        for mail in self:
            email_from = self.env.user.login
            email_to = mail.approval_id.user_id.login
            subject = 'You have a RFQ need approval'
            message = """
                        <html>
                            <head>
                                Dear %s,
                            </head></br>
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<body>
                                You have a RFQ (<a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a>) waiting for your approval.<br/><br/>
                                Requestor : %s. <br/>
                                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong>Thank You</strong>
                            </body>
                        <html>""" % (mail.approval_id.user_id.name,mail.id,mail.name,self.env.user.name)
            mail_vals['email_from'] = email_from
            mail_vals['email_to'] = email_to
            mail_vals['subject'] = subject
            mail_vals['body_html'] = message
            self.env['mail.mail'].create(mail_vals)
        return True

    # Shipment notification template
    @api.multi
    def shipment_notification_template(self):
        for order in self:
            for line in order.order_line:
                if line.receive_date:
                    formatted_date = datetime.strptime(line.receive_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%m-%Y')
                else:
                    formatted_date = ''
                for picking in order.picking_ids:
                    mail_vals = {}
                    if picking and order.approval_id.user_id:
                        partner_id = self.env['res.partner'].search([('name', '=', order.approval_id.user_id.name)])
                        email_from = self.env.user.login
                        subject = 'You have an incoming item from ' + order.name
                        message = """
                                            <html>
                                                <head>
                                                    Dear %s,
                                                </head>
                                                <body>
                                                    You will have an incoming item (<a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>) in %s from RFQ.<br/><br/>
                                                    <strong>Thank You,</strong>
                                                </body>
                                            <html>""" % (order.approval_id.user_id.name, picking.id, picking.name, formatted_date)
                        mail_vals['subject'] = subject
                        mail_vals['body'] = '<pre>%s</pre>' % message
                        mail_vals['email_from'] = email_from
                        mail_vals['partner_ids'] = [(6, 0, [partner_id.id])],
                        mail_vals['needaction_partner_ids'] = [(6, 0, [partner_id.id])]
                        thread_pool = self.env['mail.message'].create(mail_vals)
                        thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
        return True

    #Mail creation for approval user
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            mail_vals = {}
            if order.approval_id.user_id:
                partner_id = self.env['res.partner'].search([('name', '=', order.approval_id.user_id.name)])
                email_from = self.env.user.login
                subject = 'You have a RFQ need approval'
                message = """
                            <html>
                                <head>
                                    Dear %s,
                                </head>
                                <body>
                                    You have a RFQ (<a href=# data-oe-model=purchase.order data-oe-id=%d>%s</a>) waiting for your approval.<br/><br/>
                                    Requestor : %s. <br/>
                                    <strong>Thank You</strong>
                                </body>
                            <html>""" % (order.approval_id.user_id.name, order.id,order.name,self.env.user.name)
                mail_vals['subject'] = subject
                mail_vals['body'] = '<pre>%s</pre>' % message
                mail_vals['email_from'] = email_from
                mail_vals['partner_ids'] = [(6, 0, [partner_id.id])],
                mail_vals['needaction_partner_ids'] = [(6, 0, [partner_id.id])]
                thread_pool = self.env['mail.message'].create(mail_vals)
                thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
                order.send_email()
                order.write({'state': 'to approve'})
        return True

    @api.multi
    def button_approve(self, force=False):
        res = super(purchase_order, self).button_approve()
        for record in self:
            # record._create_picking()
            # if record.company_id.po_lock == 'lock':
            #     record.write({'state': 'done'})
            if record.approval_id.user_id == self.env.user:
                record.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
            record.shipment_notification_template()
        return res

    @api.multi
    def button_reject(self):
        for record in self:
            if record.approval_id.user_id == self.env.user:
                record.write({'state': 'reject'})
        return True

    # Vendor bill notification scheduler
    @api.multi
    def vendor_bill_notification_scheduler(self):
        for order in self.search([]):
            for invoice in order.invoice_ids:
                before_week = str(datetime.now() - relativedelta(weeks=1))[:10]

                mail_vals = {}
                if invoice and invoice.date_due > before_week and not order.is_vendor_bill and order.approval_id.user_id:
                    formatted_date = datetime.strptime(invoice.date_due, DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%m-%Y')
                    partner_id = self.env['res.partner'].search([('name', '=', order.approval_id.user_id.name)])
                    email_from = self.env.user.login
                    subject = 'You have vendor invoice that you need to pay.'
                    message = """
                                        <html>
                                            <head>
                                                Dear %s,
                                            </head>
                                            <body>
                                                You have a vendor invoice from (<a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>) with due date %s.<br/><br/>
                                                Requestor : %s. <br/>
                                                <strong>Thank You,</strong>
                                            </body>
                                        <html>""" % (order.approval_id.user_id.name, invoice.id, order.name, formatted_date, self.env.user.name)
                    mail_vals['subject'] = subject
                    mail_vals['body'] = '<pre>%s</pre>' % message
                    mail_vals['email_from'] = email_from
                    mail_vals['partner_ids'] = [(6, 0, [partner_id.id])],
                    mail_vals['needaction_partner_ids'] = [(6, 0, [partner_id.id])]
                    thread_pool = self.env['mail.message'].create(mail_vals)
                    thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
                    order.write({'is_vendor_bill': True})
        return True

    # Unreceived notification scheduler
    @api.multi
    def unreceived_notification_scheduler(self):
        for order in self.search([]):
            for line in order.order_line:
                mail_vals = {}
                if line.receive_date and line.receive_date == str(datetime.now())[:10] and not order.is_shipped and order.approval_id.user_id and not order.is_unreceived:
                    partner_id = self.env['res.partner'].search([('name', '=', order.approval_id.user_id.name)])
                    email_from = self.env.user.login
                    subject = 'You have an item to receive'
                    message = """
                                        <html>
                                            <head>
                                                Dear %s,
                                            </head>
                                            <body>
                                                You have a purchase order %s waiting to receive.<br/><br/>
                                                Requestor : %s. <br/>
                                                <strong>Thank You,</strong>
                                            </body>
                                        <html>""" % (
                        order.approval_id.user_id.name, order.name, self.env.user.name)
                    mail_vals['subject'] = subject
                    mail_vals['body'] = '<pre>%s</pre>' % message
                    mail_vals['email_from'] = email_from
                    mail_vals['partner_ids'] = [(6, 0, [partner_id.id])],
                    mail_vals['needaction_partner_ids'] = [(6, 0, [partner_id.id])]
                    thread_pool = self.env['mail.message'].create(mail_vals)
                    thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
                    order.write({'is_unreceived': True})
        return True

purchase_order()

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    receive_date = fields.Date(string='Receive Date', default=date.today())
    approve_check = fields.Boolean(compute='_compute_approve_check', string='Approve Check')

    def _compute_approve_check(self):
        for record in self:
            if record.order_id:
                record.approve_check = record.order_id.approve_check
            else:
                record.approve_check = False

purchase_order_line()