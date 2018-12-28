# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import time
from datetime import datetime
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import odoo.addons.decimal_precision as dp



class AdditionalCharges(models.Model):

    _name = 'additional.charges.po'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    name = fields.Char('Name')
    description = fields.Char('Description')
    amount = fields.Float('Amount')

    @api.multi
    def compute_additional_charge(self):
        self.ensure_one()
        if self.purchase_id.additional_charges_ids:
            additional_charges_amount = 0.0
            for charge in self.purchase_id.additional_charges_ids:
                additional_charges_amount += charge.amount

            product_id = self.env['product.product'].search([
                ('name', '=', 'Additional Charges')], limit=1)
            if not product_id:
                product_id = self.env['product.product'].create({'name': 'Additional Charges',
                                                                 'type': 'service'})
            purchase_line_obj = self.env['purchase.order.line']
            purchase_line_rec = purchase_line_obj.search([('product_id', '=', product_id.id),
                                                          ('order_id', '=', self.purchase_id.id)])
            if not purchase_line_rec:
                purchase_line_obj.create({
                    'name': _('Additional Charges: %s') % (time.strftime('%m %Y'),),
                    'price_unit': additional_charges_amount,
                    'product_qty': 1,
                    'order_id': self.purchase_id.id,
                    'discount': 0.0,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_uom': product_id.uom_id.id,
                    'product_id': product_id.id,
                })
            else:
                purchase_line_rec.price_unit = additional_charges_amount

    @api.model
    def create(self, vals):
        res = super(AdditionalCharges, self).create(vals)
        res.compute_additional_charge()
        return res

    @api.multi
    def write(self, vals):
        res = super(AdditionalCharges, self).write(vals)
        self.compute_additional_charge()
        return res


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    additional_charges_ids = fields.One2many('additional.charges.po','purchase_id','Additional Charges')
    amount_additional_charge = fields.Monetary(string='Additional Charges', store=True, readonly=True, compute='_amount_additional_charge')

    @api.depends('additional_charges_ids.amount')
    def _amount_additional_charge(self):
        for order in self:
            amount_additional = 0.0
            for line in order.additional_charges_ids:
                amount_additional += line.amount
            order.update({
                'amount_additional_charge': amount_additional,
                # 'amount_total': order.amount_total + amount_additional,
            })

    @api.depends('order_line.price_total','additional_charges_ids.amount')
    def _amount_all(self):
        super(PurchaseOrder, self)._amount_all()
        for order in self:
            order.update({'amount_total': order.amount_total + order.amount_additional_charge,})

