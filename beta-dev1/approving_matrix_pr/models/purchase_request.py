# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning

class purchase_request(models.Model):
    _inherit = 'purchase.request'

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_all(self):
        total = 0
        for rec in self:
            for line in rec.line_ids:
                total = total + line.price_subtotal
                rec.price_total = total


    @api.depends('price_total','approving_matrix_id')
    def _get_approval_matrix_line(self):
        for rec in self:
            rec.approving_matrix_line_ids = False
            approval_matrix_lines = []
            if rec.approving_matrix_id:

                if rec.approving_matrix_id.matrix_type == 'amount':
                    approval_lines = rec.approving_matrix_id.line_ids.filtered(lambda r: r.min_amount < rec.price_total)
                else:
                    approval_lines = rec.approving_matrix_id.line_ids

                for line in approval_lines:
                    approval_matrix_lines.append([0, 0, {
                        'employee_ids': [(6,0, line.employee_ids.ids)],
                        'name': line.name,
                        'min_amount': line.min_amount,
                        'max_amount':line.max_amount,
                        'approved': False,
                        }
                    ])

            if approval_matrix_lines:
                rec.approving_matrix_line_ids = approval_matrix_lines


    approving_matrix_id = fields.Many2one('pr.approving.matrix', String="Approving Matrix", required = True, copy=False,
                                          ondelete="restrict",)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    price_total = fields.Monetary(compute='_compute_amount_all', string='Total Amount', store=True, copy=False)

    approving_matrix_line_ids = fields.One2many('pr.approving.matrix.line','purchase_request_id', string="Approving Matrix Lines",
                                                 compute="_get_approval_matrix_line", store=True, copy=False)
                                                 
    is_multiline_approval = fields.Boolean(string="Approve", default= False, copy=False)
    is_button_rejected = fields.Boolean(string="Reject", default= False, copy=False)


    @api.multi
    def send_mail_pr_approval_process(self, receiver):
        view = 'Purchase Request'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        link = base_url + '/web#id=%s&view_type=form&model=purchase.request' % self.id

        receivers = ''
        for partner in receiver:
            receivers += partner.name + ','

        body_dynamic_html = '<p>Dear %s </p>' % receivers
        body_dynamic_html += '<p> Request you to approve PR: %s </p>' % self.name
        body_dynamic_html += '<p> Requestor: %s </p>' % self.create_uid.name

        body_dynamic_html += '<div style = "margin: 16px;">\
                                    <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;\
                                     color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; \
                                     margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; \
                                     cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;\
                                     border: 1px solid #875A7B; border-radius:3px">View %s</a></div><p> Thank You.</div>' % (link, view)


        thread_pool = self.env['mail.message'].sudo().create({
            'subject':'You have a PR need approval',
            'body': body_dynamic_html,
            'model': 'purchase.request',
            'partner_ids':[(6,0,receiver.mapped('partner_id').ids)],
            'needaction_partner_ids': [(6,0,receiver.mapped('partner_id').ids)],
        })

        thread_pool.needaction_partner_ids = [(6, 0, receiver.mapped('partner_id').ids)]

    @api.multi
    def button_to_approve(self):
        """ send request for approve purchase request """
        lines = self.approving_matrix_line_ids.filtered(lambda r: r.approved == False)
        for line in lines:
            if line.employee_ids and len(line.employee_ids) > 0:
                user_ids = line.employee_ids.mapped('user_id')
                """ create notification in discussion panel """
                if user_ids:
                    self.send_mail_pr_approval_process(user_ids)
                    break

        if lines:
            return super(purchase_request, self).button_to_approve()
        else:
            return super(purchase_request, self).button_approved()

    @api.multi
    def button_approved(self):
        """ apprpved purchase request """
        #check multiple approving_matrix_line
        for record in self:
            approving_matrix_line = len(record.approving_matrix_line_ids)
            if approving_matrix_line > 1:
                self.is_multiline_approval = True
                
        for record in self:
            approved_pr_line = True
            for line_id in record.line_ids:
                pr_line_ids = line_id.approving_matrix_line_ids.filtered(lambda r: r.line_approved == False)
                if pr_line_ids:
                    approved_pr_line = False
                    break
            if approved_pr_line:
                return super(purchase_request, self).button_approved()

            for line in record.approving_matrix_line_ids.filtered(lambda r: r.approved == False):
                if line.employee_ids and len(line.employee_ids) > 0:
                    user_ids = line.employee_ids.mapped('user_id').ids
                    if self._uid in user_ids:
                        line.write({'approved':True})
                        self.button_to_approve()
                        break
                    else:
                        raise Warning(_("You don't have access to approve this!"))
                else:
                    raise Warning(_("Only Administrator can approve this!"))
            else:
                return super(purchase_request, self).button_approved()
                
                
    @api.multi
    def button_rejected(self):
        self.state = 'rejected'
        #check multiple approving_matrix_line
        for record in self:
            approving_matrix_line = len(record.approving_matrix_line_ids)
            if approving_matrix_line > 1:
                self.is_button_rejected = True    
        return True


