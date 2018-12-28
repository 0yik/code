# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'


    @api.depends('product_qty','estimated_price')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = rec.product_qty * rec.estimated_price


    @api.depends('price_subtotal','approving_matrix_id')
    def _get_approval_matrix_line(self):
        for rec in self:
            rec.approving_matrix_line_ids = False
            approval_matrix_lines = []
            if rec.approving_matrix_id:

                if rec.approving_matrix_id.matrix_type == 'amount':
                    approval_lines = rec.approving_matrix_id.line_ids.filtered(
                        lambda r: r.min_amount < rec.price_subtotal)
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


    estimated_price = fields.Float(String = 'Estimated Price')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True)

    approving_matrix_id = fields.Many2one('pr.approving.matrix', related="request_id.approving_matrix_id",
                                          String="Approving Matrix", required=True, copy=False, store=True)

    approving_matrix_line_ids = fields.One2many('pr.approving.matrix.line', 'purchase_request_line_id',
                        string="Approving Matrix Lines", compute="_get_approval_matrix_line", store=True, copy=False)


    @api.onchange('product_id')
    def onchange_request_product_id(self):
        for rec in self:
            rec.estimated_price = 0
            if rec.product_id:
                rec.estimated_price = rec.product_id.list_price

    @api.multi
    def send_mail_pr_line_approval_process(self, receiver):
        view = 'Purchase Request Line'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        link = base_url + '/web#id=%s&view_type=form&model=purchase.request.line' % self.id

        receivers = ''
        for partner in receiver:
            receivers += partner.name + ','

        body_dynamic_html = '<p>Dear %s </p>' % receivers
        body_dynamic_html += '<p> Request you to approve PR Line: %s </p>' % self.name
        body_dynamic_html += '<p> Requestor: %s </p>' % self.create_uid.name

        body_dynamic_html += '<div style = "margin: 16px;">\
                                        <a href=%s style = "padding: 5px 10px; font-size: 12px; line-height: 18px;\
                                         color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; \
                                         margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; \
                                         cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B;\
                                         border: 1px solid #875A7B; border-radius:3px">View %s</a></div><p> Thank You.</div>' % (
        link, view)

        thread_pool = self.env['mail.message'].sudo().create({
            'subject': 'You have a PR Line need approval',
            'body': body_dynamic_html,
            'model': 'purchase.request.line',
            'partner_ids': [(6, 0, receiver.mapped('partner_id').ids)],
            'needaction_partner_ids': [(6, 0, receiver.mapped('partner_id').ids)],
        })

        thread_pool.needaction_partner_ids = [(6, 0, receiver.mapped('partner_id').ids)]


    @api.multi
    def button_approved(self):
        for record in self:

            for line in record.approving_matrix_line_ids.filtered(lambda r: r.line_approved == False):
                if line.employee_ids and len(line.employee_ids) > 0:
                    user_ids = line.employee_ids.mapped('user_id').ids
                    if self._uid in user_ids:
                        line.write({'line_approved':True})
                        break
                    else:
                        raise Warning(_("You don't have access to approve this!"))
                else:
                    raise Warning(_("Only Administrator can approve this!"))
            else:
                #record.approving_matrix_line_ids.write({'line_approved': True})
                return super(purchase_request_line, self).button_approved()


            for line in record.approving_matrix_line_ids.filtered(lambda r: r.line_approved == False):
                if line.employee_ids and len(line.employee_ids) > 0:
                    user_ids = line.employee_ids.mapped('user_id')
                    """ create notification in discussion panel """
                    if user_ids:
                        self.send_mail_pr_line_approval_process(user_ids)
                        break
            else:
                #record.approving_matrix_line_ids.write({'line_approved': True})
                return super(purchase_request_line, self).button_approved()


    @api.model
    def hide_approve_button(self):
        try:
            if self.env.ref('purchase_request.action_approve_puchse_request'):
                self.env.ref('purchase_request.action_approve_puchse_request').unlink()
        except:
            pass





