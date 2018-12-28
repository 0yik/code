from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError

class sale_order(models.Model):
    _inherit = 'sale.order'

    using_discount = fields.Boolean('use discount',compute='_compute_using_discount')
    discount_promotion_service = fields.Monetary('Discount',compute='_compute_discount_promotion_service')
    have_promo_line = fields.Boolean(compute='_compute_have_promo_line',string='have promo')

    @api.multi
    def action_confirm(self):
        partner = self.partner_id
        if partner.property_payment_term_id:
            days = 0
            if partner.property_payment_term_id.id == self.env.ref('account.account_payment_term_15days').id:
                days = 15
            if partner.property_payment_term_id.id == self.env.ref('account.account_payment_term_net').id:
                days = 30
            if days:
                domain = [('id','<',self.id),('partner_id', '=', partner.id), ('state', '=', 'sale'), ('confirmation_date', '<=',
                                                                                     datetime.strftime(
                                                                                         datetime.now() - relativedelta(
                                                                                             days=days),
                                                                                         DEFAULT_SERVER_DATETIME_FORMAT))]
                sales = self.search(domain, order="confirmation_date asc")
                flag = True
                tmp_sale = False
                for sale in sales:
                    if not sale.invoice_ids:
                        flag = False
                        tmp_sale = sale
                        break
                    else:
                        for inv in sale.invoice_ids:
                            if inv.state in ['draft','open']:
                                flag = False
                                tmp_sale = sale
                                break
                if not flag:
                    raise ValidationError(_("You need to paid for Sale order %s") % tmp_sale.name)
        res = super(sale_order, self).action_confirm()
        return res

    @api.multi
    @api.depends('order_line')
    def _compute_have_promo_line(self):
        for order in self:
            for line in order.order_line:
                if line.product_id.default_code == 'PS':
                    order.have_promo_line = True
                    break

    @api.one
    @api.depends('order_line.price_total','using_discount')
    def _compute_discount_promotion_service(self):
        disc_val = 0
        for line in self.order_line:
            if line.product_id.default_code == 'PS':
                disc_val += line.price_unit
                if not line.is_promo:
                    line.write({
                        'is_promo':True
                    })
        self.discount_promotion_service = disc_val

    @api.multi
    def _compute_using_discount(self):
        printout_conf = self.env['ir.values'].get_default('sale.config.settings', 'printout_sale_order')
        if printout_conf == 'unused':
            for order in self:
                order.using_discount = True
        else:
            for order in self:
                order.using_discount = False
    # self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting')

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    is_promo = fields.Boolean('Is Promo',default=False)
    using_discount = fields.Boolean('use discount',related='order_id.using_discount')

