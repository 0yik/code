from odoo import models, fields, api, _
from odoo import SUPERUSER_ID
from odoo.exceptions import Warning
from datetime import datetime
from lxml import etree

class purchase_request(models.Model):
    _inherit = 'purchase.request'

    product_ctg = fields.Many2one('pr.approving.matrix', string='Approval', track_visibility='onchange',required=True)
    approved_ids = fields.Many2many('pr.approving.matrix.line')
    check_access_request = fields.Boolean('Check Approval', compute='_compute_check_access_analytic_account',default=False)
    user_id_line_approved = fields.Many2many('res.users')

    def total_amout(self):
        amount = 0.0
        for line in self.line_ids:
            if line.amount:
                amount += line.amount
        return amount

    def _compute_check_access_analytic_account(self):
        approved_id = self.check_next_approver()
        if approved_id and approved_id.employee_ids.mapped('user_id'):
            if self._uid in approved_id.employee_ids.mapped('user_id').ids and self._uid in self.user_id_line_approved.ids:
                self.check_access_request = True
            else:
                self.check_access_request = False
        else:
            self.check_access_request = True

    @api.multi
    def button_draft(self):
        super(purchase_request, self).button_draft()
        self.approved_ids = None

    @api.multi
    def button_to_approve(self):
        res = super(purchase_request, self).button_to_approve()
        amount = self.total_amout()
        if self.product_ctg:
            self.approved_ids = self.product_ctg.line_ids.filtered(lambda r: r.check_amount(amount) == True)
        approved_id = self.check_next_approver()
        if approved_id:
            self.user_id_line_approved = approved_id.employee_ids.mapped('user_id')
            user_list = ""
            for user in self.user_id_line_approved:
                user_list += "%s " % (user.name)
            self.create_comment_log("Waiting users approve: %s" % (user_list))
            self.send_mail_next_approved(approved_id)
        return res

    @api.multi
    def button_approved(self):
        for record in self:
            if not record.product_ctg:
                super(purchase_request, record).button_approved()
            else:
                approved_id = self.check_next_approver()
                if approved_id:
                    self.user_id_line_approved = [(3,self._uid)]
                    self.create_comment_log("Approved by %s"%(self.env.user.name))
                    if not self.user_id_line_approved:
                        self.approved_ids = [(3,approved_id.id)]
                    else:
                        return True
                if not self.check_next_approver():
                    super(purchase_request, record).button_approved()
                else:
                    approved_id = self.check_next_approver()
                    self.user_id_line_approved = approved_id.employee_ids.mapped('user_id')
                    user_list = ""
                    for user in self.user_id_line_approved:
                        user_list += "%s "%(user.name)
                    self.create_comment_log("Waiting users approved %s" % (user_list))
                    self.send_mail_next_approved(approved_id)
                    return True


    def check_next_approver(self):
        for i in range(0, len(self.approved_ids)):
            approved_id = self.approved_ids.search([('id','in',self.approved_ids.ids)],order='sequence ASC',limit=1)
            if approved_id.employee_ids and approved_id.employee_ids.mapped('user_id'):
                return approved_id
            else:
                self.approved_ids = [(3, approved_id.id)]

    def send_mail_next_approved(self,approved_id):
        user_ids = approved_id.employee_ids.mapped('user_id')
        for user in user_ids:
            template = self.get_to_approve_pr_template(user)
            self.send_mail(template, user)

    def create_comment_log(self,comment):
        mail_message_obj = self.env['mail.message']
        time_now = datetime.today()
        subtype_id = self.env['mail.message.subtype'].search([('name','=','Note')]).id or False
        vals = {
            'model' : 'purchase.request',
            'message_type' : 'comment',
            'res_id'       : self.id,
            'record_name'  : self.name,
            'body'         : comment,
            'date'         : time_now,
            'subtype_id'   : subtype_id,
        }
        mail_message_obj.create(vals)

    def send_mail(self, template, user):
        partner_id = self.env['res.partner'].search([('name', '=', user.name)])
        mail_message = {
            'subject': template['subject'],
            'body': template['body_html'],
            'partner_ids': [(6, 0, [partner_id.id])],
            'needaction_partner_ids': [(6, 0, [partner_id.id])]
        }
        thread_pool = self.env['mail.message'].create(mail_message)
        thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
        self.env['mail.mail'].create(template)

    def get_to_approve_pr_template(self, to_user):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = base_url + '/web#id=%s&view_type=form&model=purchase.request' % (self.id)
        email_from = self.company_id.email or 'Administrator <admin@example.com>'
        email_to = to_user.email
        subject = 'You have a Purchase Request need approval'
        message = """
            <html>
                <head>
                    Dear %s,
                </head>
                <body>
                    You have a Purchase Request *PR No %s (<a href="%s" target="_blank">Clickable link</a>)waiting for your approval.<br/><br/>
                    Vendor : %s. <br/>
                    Untaxed Amount : %s<br/><br/>
                    <strong>Thank you</strong>
                </body>
            <html>""" % (to_user.name, self.name,url, self.requested_by.name,self.total_amout)

        return {
            'state': 'outgoing',
            'subject': subject,
            'body_html': '<pre>%s</pre>' % message,
            'email_to': email_to,
            'email_from': email_from,
        }

class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'

    amount = fields.Float(string="Amount")

    @api.onchange('product_id','product_qty')
    def onchange_product_id(self):
        for record in self:
            if record.product_id and record.product_qty:
                record.amount = record.product_id.lst_price * record.product_qty
