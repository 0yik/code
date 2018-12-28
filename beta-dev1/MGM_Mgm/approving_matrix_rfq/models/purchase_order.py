# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    is_multiline_approval = fields.Boolean(string="Approve", default= False, copy=False)
    is_button_rejected = fields.Boolean(string="Reject", default= False, copy=False)
    
    @api.depends('amount_total','approving_matrix_id')
    def _get_approval_matrix_line(self):
        for rec in self:
            rec.approving_matrix_line_ids = False
            approval_matrix_lines = []
            if rec.approving_matrix_id:
                if rec.approving_matrix_id.matrix_type == 'amount':
                    approval_lines = rec.approving_matrix_id.line_ids.filtered(lambda r: r.min_amount < rec.amount_total)
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
    approving_matrix_line_ids = fields.One2many('pr.approving.matrix.line','purchase_order_id', string="Approving Matrix Lines",
                                                 compute="_get_approval_matrix_line", store=True, copy=False)

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('waiting_for_approval', 'RFQ Waiting for Approval'),
        ('rfq_approved', 'RFQ Approved'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('rfq_reject', 'RFQ Rejected')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')


    @api.multi
    def send_mail_pr_approval_process(self, receiver):
        view = 'RFQ'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        link = base_url + '/web#id=%s&view_type=form&model=purchase.order' % self.id

        receivers = ''
        for partner in receiver:
            receivers += partner.name + ','

        body_dynamic_html = '<p>Dear %s </p>' % receivers
        body_dynamic_html += '<p> Request you to approve RFQ: %s </p>' % self.name
        body_dynamic_html += '<p> Requestor: %s </p>' % self.create_uid.name

        body_dynamic_html += '<div style = "margin: 16px;">\
                                    <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;\
                                     color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; \
                                     margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; \
                                     cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;\
                                     border: 1px solid #875A7B; border-radius:3px">View %s</a></div><p> Thank You.</div>' % (link, view)

        thread_pool = self.env['mail.message'].sudo().create({
            'subject':'You have a RFQ need approval',
            'body': body_dynamic_html,
            'model': 'purchase.order',
            'partner_ids':[(6,0,receiver.mapped('partner_id').ids)],
            'needaction_partner_ids': [(6,0,receiver.mapped('partner_id').ids)],
        })

        thread_pool.needaction_partner_ids = [(6, 0, receiver.mapped('partner_id').ids)]

    @api.multi
    def request_rfq_approve(self):
        lines = self.approving_matrix_line_ids.filtered(lambda r: r.approved == False)
        if lines:
            self.state = 'waiting_for_approval'
        else:
            self.state = 'rfq_approved'
            return True

        for line in lines:
            if line.employee_ids and len(line.employee_ids) > 0:
                user_ids = line.employee_ids.mapped('user_id')
                """ create notification in discussion panel """
                if user_ids:
                    self.send_mail_pr_approval_process(user_ids)
                    break

    @api.multi
    def rfq_approved(self):
        for record in self:
            #check multiple approving_matrix_line
            approving_matrix_line = len(record.approving_matrix_line_ids)
            if approving_matrix_line > 1:
                self.is_multiline_approval = True
                
            for line in record.approving_matrix_line_ids.filtered(lambda r: r.approved == False):
                if line.employee_ids and len(line.employee_ids) > 0:
                    user_ids = line.employee_ids.mapped('user_id').ids
                    if self._uid in user_ids:
                        line.write({'approved':True})
                        self.request_rfq_approve()
                        break
                    else:
                        raise Warning(_("You don't have access to approve this!"))
                else:
                    raise Warning(_("Only Administrator can approve this!"))
            else:
                self.state = 'rfq_approved'

    @api.multi
    def button_confirm(self):
        """ Added new state to consider in def button_confirm of default purchase """
        for order in self:
            if order.state not in ['draft', 'rfq_approved', 'sent']:
                continue
            order._add_supplier_to_product()
            order.button_approve()

    @api.multi
    def rfq_rejected(self):
        self.state = 'rfq_reject'
        for record in self:
            approving_matrix_line = len(record.approving_matrix_line_ids)
            if approving_matrix_line > 1:
                self.is_button_rejected = True    
        return True


