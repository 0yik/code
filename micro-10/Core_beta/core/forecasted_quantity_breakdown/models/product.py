# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qty_incoming_dummy = fields.Float(
        related='incoming_qty',
        string='Quantity Incoming',
        help='Count of incoming qty.', )
    qty_outgoing_dummy = fields.Float(
        related='outgoing_qty',
        string='Quantity Outgoing',
        help='Count of outgong qty.', )

    @api.multi
    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
            products = self.mapped('product_variant_ids')
            action['domain'] = [
                ('picking_id.picking_type_id.code', '=', 'incoming'),
                ('location_id.usage', '!=', 'internal'),
                ('location_dest_id.usage', '=', 'internal'),
                ('product_id', 'in', products.ids)]
        return action

    @api.multi
    def action_open_incoming_shipment(self):
        return self._get_action('stock.action_receipt_picking_move')

    @api.multi
    def get_action_outgoing(self):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref('forecasted_quantity_breakdown.action_do_picking_move').read()[0]
        if self:
            action['display_name'] = self.display_name
            products = self.mapped('product_variant_ids')
            action['domain'] = [
                ('picking_id.picking_type_id.code', '=', 'outgoing'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'customer'),
                ('product_id', 'in', products.ids)]
        return action


ProductTemplate()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_action_product(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
            #products = self.mapped('product_variant_ids')
            action['domain'] = [
                ('picking_id.picking_type_id.code', '=', 'incoming'),
                ('location_id.usage', '!=', 'internal'),
                ('location_dest_id.usage', '=', 'internal'),
                ('product_id', 'in', self.ids)]
        return action

    @api.multi
    def action_open_incoming_shipment_product(self):
        return self._get_action_product('stock.action_receipt_picking_move')

    @api.multi
    def get_action_outgoing_product(self):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref('forecasted_quantity_breakdown.action_do_picking_move').read()[0]
        if self:
            action['display_name'] = self.display_name
            #products = self.mapped('product_variant_ids')
            action['domain'] = [
                ('picking_id.picking_type_id.code', '=', 'outgoing'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'customer'),
                ('product_id', 'in', self.ids)]
        return action


ProductProduct()
