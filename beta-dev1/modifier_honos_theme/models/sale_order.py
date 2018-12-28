# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    booking_line_id = fields.Many2one('booking.order.line')
    is_deposit_for_rent = fields.Boolean()

    @api.multi
    def unlink(self):
        self.mapped('booking_line_id').unlink()
        return super(SaleOrderLine, self).unlink()

    @api.multi
    def _action_procurement_create(self):
        # restrict to create procuremnt for rented product lines
        new_self = self.filtered(lambda l: not l.booking_line_id)
        return super(SaleOrderLine, new_self)._action_procurement_create()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    booking_id = fields.Many2one('booking.order')

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, rent_days=None, tot_days=0, rental_price=0, **kwargs):
        self.ensure_one()
        if line_id and add_qty == None and set_qty == 0:
            self.order_line.filtered(lambda l: l.id == line_id and l.booking_line_id).booking_line_id.unlink()

        values = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)

        if rent_days:
            refundable_deposit_product = self.env.ref('pos_rental.product_product_advance_payment')
            deposite_val = self.env['website'].search([])[0].website_advance_deposit
            new_line = self.env['sale.order.line'].create({
            'order_id':self.id,
            'product_id':refundable_deposit_product.id,
            'product_uom_qty':1.0,
            'product_uom':refundable_deposit_product.uom_id.id,
            'price_unit':(rental_price * deposite_val)/100,
            'customer_lead':0.0,
            'is_deposit_for_rent': True,
            })

            if not self.booking_id:
                booking = self.env['booking.order'].create({
                    'partner_id': self.partner_id.id,
                    'def_start_date': rent_days.get('start'),
                    'def_end_date': rent_days.get('end'),
                })
                self.booking_id = booking.id
            if not line_id and values.get('line_id'):
                booking_line = self.env['booking.order.line'].create({
                    'product_id': product_id,
                    'start_date': rent_days.get('start'),
                    'end_date': rent_days.get('end'),
                    'actual_start_date': rent_days.get('start'),
                    'actual_end_date': rent_days.get('end'),
                    'order_id': self.booking_id.id,
                    'total_days':tot_days,
                    'product_qty': values.get('quantity') or 1,
                })
                self.order_line.filtered(lambda l: l.id == values.get('line_id')).write({'booking_line_id': booking_line.id, 'price_unit': rental_price})
        if rental_price:
            self.order_line.filtered(lambda l: l.id == values.get('line_id')).write({'price_unit': rental_price})

        return values

class webBookingOrderLine(models.Model):
    _inherit = 'booking.order.line'

    total_days = fields.Char(string='No of days')

class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        """ Return the current sale order after mofications specified by params.
        :param bool force_create: Create sale order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sale order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
        :returns: browse record for the current sale order
        """
        self.ensure_one()
        partner = self.env.user.partner_id
        sale_order_id = request.session.get('sale_order_id')

        if not sale_order_id:
            last_order = partner.last_website_so_id
            available_pricelists = self.get_pricelist_available()
            # Do not reload the cart of this user last visit if the cart is no longer draft or uses a pricelist no longer available.
            sale_order_id = last_order.state == 'draft' and last_order.pricelist_id in available_pricelists and last_order.id

        pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id

        if self.env['product.pricelist'].browse(force_pricelist).exists():
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True

        if not self._context.get('pricelist'):
            self = self.with_context(pricelist=pricelist_id)

        # Test validity of the sale_order_id
        sale_order = self.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None

        # create so if needed
        if not sale_order and (force_create or code):
            # TODO cache partner_id session
            pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
            so_data = self._prepare_sale_order_values(partner, pricelist)
            sale_order = self.env['sale.order'].sudo().create(so_data)

            # set fiscal position
            if request.website.partner_id.id != partner.id:
                sale_order.onchange_partner_shipping_id()
            else: # For public user, fiscal position based on geolocation
                country_code = request.session['geoip'].get('country_code')
                if country_code:
                    country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
                    fp_id = request.env['account.fiscal.position'].sudo()._get_fpos_by_region(country_id)
                    sale_order.fiscal_position_id = fp_id
                else:
                    # if no geolocation, use the public user fp
                    sale_order.onchange_partner_shipping_id()

            request.session['sale_order_id'] = sale_order.id

            if request.website.partner_id.id != partner.id:
                partner.write({'last_website_so_id': sale_order.id})

        if sale_order:
            # case when user emptied the cart
            if not request.session.get('sale_order_id'):
                request.session['sale_order_id'] = sale_order.id

            # check for change of pricelist with a coupon
            pricelist_id = pricelist_id or partner.property_product_pricelist.id

            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position_id.id

                # change the partner, and trigger the onchange
                sale_order.write({'partner_id': partner.id})
                sale_order.onchange_partner_id()
                sale_order.onchange_partner_shipping_id() # fiscal position
                sale_order['payment_term_id'] = self.sale_get_payment_term(partner)

                # check the pricelist : update it if the pricelist is not the 'forced' one
                values = {}
                if sale_order.pricelist_id:
                    if sale_order.pricelist_id.id != pricelist_id:
                        values['pricelist_id'] = pricelist_id
                        update_pricelist = True

                # if fiscal position, update the order lines taxes
                if sale_order.fiscal_position_id:
                    sale_order._compute_tax_id()

                # if values, then make the SO update
                if values:
                    sale_order.write(values)

                # check if the fiscal position has changed with the partner_id update
                recent_fiscal_position = sale_order.fiscal_position_id.id
                if flag_pricelist or recent_fiscal_position != fiscal_position:
                    update_pricelist = True

            if code and code != sale_order.pricelist_id.code:
                code_pricelist = self.env['product.pricelist'].sudo().search([('code', '=', code)], limit=1)
                if code_pricelist:
                    pricelist_id = code_pricelist.id
                    update_pricelist = True
            elif code is not None and sale_order.pricelist_id.code:
                # code is not None when user removes code and click on "Apply"
                pricelist_id = partner.property_product_pricelist.id
                update_pricelist = True

            # update the pricelist
            if update_pricelist:
                request.session['website_sale_current_pl'] = pricelist_id
                values = {'pricelist_id': pricelist_id}
                sale_order.write(values)
                for line in sale_order.order_line:
                    if line.exists():
                        sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, rental_price=line.price_unit, add_qty=0)

        else:
            request.session['sale_order_id'] = None
            return self.env['sale.order']

        return sale_order
