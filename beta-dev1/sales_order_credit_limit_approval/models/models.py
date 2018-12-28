from odoo import models, fields, api,_
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError

class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    credit_limit_approver = fields.Many2many('res.users',string='Credit Limit Approver')

    @api.multi
    def set_credit_limit_approver(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'credit_limit_approver', self.credit_limit_approver.ids)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approved_by = fields.Many2one('res.users',string='Approved By')
    show_approve_over_limit = fields.Boolean(compute="_show_approve_over_limit")

    @api.multi
    def _show_approve_over_limit(self):
        user_ids = self.env['ir.values'].get_default('sale.config.settings', 'credit_limit_approver') or []
        for order in self:
            if self.env.user.id in user_ids:
                order.show_approve_over_limit = True


    @api.multi
    def action_approve_limit(self):
        for order in self:
            order.write({'approved_by': self.env.user.id})
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True

    @api.one
    def check_limit(self):
        partner = self.partner_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.\
            search([('partner_id', '=', partner.id),
                    ('account_id.user_type_id.name', 'in',
                    ['Receivable', 'Payable']),
                    ('full_reconcile_id', '=', False)])

        debit, credit = 0.0, 0.0
        today_dt = datetime.strftime(datetime.now().date(), DF)
        for line in movelines:
            if line.date_maturity < today_dt:
                credit += line.debit
                debit += line.credit

        if (credit - debit + self.amount_total) > partner.credit_limit:
            if not partner.over_credit:
                # msg = 'Can not confirm Sale Order,Total mature due Amount ' \
                #       '%s as on %s !\nCheck Partner Accounts or Credit ' \
                #       'Limits !' % (credit - debit, today_dt)
                msg = 'You need approval to confirm this sales order.'
                raise UserError(_('Credit Over Limits !\n' + msg))
            else:
                partner.write({
                    'credit_limit': credit - debit + self.amount_total})
                return True
        else:
            return True

    # @api.multi
    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     for order in self:
    #         order.check_limit()
    #     return res