# coding=utf-8
from odoo import api, models, fields, _

class SaleOrderModifier(models.Model):
    _inherit = "sale.order"

    quotation_reference = fields.Char(string='Quotation Reference')
    cancel_reason = fields.Text('Cancellation Reason')


    @api.multi
    def action_confirm(self):
        for order in self:
            if order.is_direct_so == False and self._context['default_is_direct_so'] == False:
                order.quotation_reference=order.name
            else:
                order.quotation_reference = ''
            name_list=order.name.split("/")
            name_list[1] = "SO"
            new_name = name_list[0] + "/" + name_list[1] + "/" + name_list[2] + "/" + name_list[3] + "/" + name_list[4]
            order.write({
                'name' : new_name,
            })
            res = super(SaleOrderModifier, self).action_confirm()
        return res

    @api.multi
    def action_cancel(self):
        return {
            'name': _('Cancel Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'cancel.sale.order.reason',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

class cancel_order(models.TransientModel):
    _name = 'cancel.sale.order.reason'

    cancel_reason = fields.Text('Cancellation Reason',required=True)

    @api.multi
    def cancel_os(self):
        if self.env.context.get('active_id'):
            sale_id = self.env.context.get('active_id')
            sale_order = self.env['sale.order'].browse(sale_id)
            if sale_order:
                sale_order.write({'state': 'cancel'})
                sale_order.cancel_reason = self.cancel_reason
        return True

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    note    = fields.Text('Note')
    franco  = fields.Char('Franco')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_so_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_so_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_so_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
        self.update(vals)

        return result

# class ResPartnerModifications(models.Model):
#     _inherit = 'res.partner'
#
#     @api.model
#     def name_search(self, name, args=None, operator='ilike', limit=100):
#         args = args or []
#         recs = self.search([])
#         print "<<<<<<<<<<<<",self._context
#         if recs:
#             if self._context.get('default_sale_order'):
#                 recs = self.search([('parent_id','=',False),('customer','=',True)])
#                 return recs.name_get()
#             elif self._context.get('default_type') in ('invoice','delivery'):
#                 print ">>>>>>>>>>>>",recs.name_get()
#                 print ">>>>>>>>>>>>",self._context.get('search_default_customer')
#                 recs = self.search([('customer', '=', True)])
#                 return recs.name_get()
#             else:
#                 return super(ResPartnerModifications, self).name_search(name, args=args, operator=operator, limit=limit)
#
#
#

