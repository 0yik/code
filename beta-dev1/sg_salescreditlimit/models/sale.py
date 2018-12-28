from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('partner_id', 'currency_id', 'amount_total')
    def get_available_credit(self):
        for order in self:
            total_amount = order.amount_total
            available_credit = order.partner_id.available_credit
            company_currency = self.env.user.sudo().company_id.currency_id
            if order.currency_id and company_currency.id != order.currency_id.id:
                available_credit = company_currency.compute(available_credit, order.currency_id)
            credit_remaining = available_credit - total_amount
            order.credit_limit = credit_remaining

    credit_limit = fields.Float(string='Available Credit', compute='get_available_credit')

    @api.multi
    def action_confirm(self):
        for order in self:
            group_id = self.env['ir.model.data'].sudo().xmlid_to_res_id('sg_salescreditlimit.group_override_limit')
            group_ids = self.env.user.groups_id.ids
            if group_id not in group_ids:
                if order.credit_limit >= 0:
                    order.write({'state':'sale'})
                else:
                    raise UserError('Credit limit exceeded, Can not confirm sales order')
            else:
                order.write({'state':'sale'})
        return super(SaleOrder,self).action_confirm()

SaleOrder()