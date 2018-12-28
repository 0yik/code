# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class account_move(models.Model):
    _inherit = 'account.move'

    currency_id = fields.Many2one('res.currency', string='Currency', required=False,
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  track_visibility='onchange')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        # if self.dest_address_id:
        #     return self.dest_address_id.property_stock_customer.id
        return self.picking_type_id.default_location_dest_id.id



class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order(self, partner):
        res = super(ProcurementOrder, self)._prepare_purchase_order(partner)
        rule = self.env['procurement.rule'].search([('action','=','buy')], limit=1)
        if rule:
            res.update({
                'picking_type_id' : rule.picking_type_id.id
            })
        return res

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def assign_picking(self):
        if 'non_assign_picking' in self._context:
            self.state = 'draft'
            return
            # self.unlink()
        return super(StockMove, self).assign_picking()


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def do_make_po(self, new_procs, product_id, needed_qty):
        bom_id = self.env['mrp.bom'].with_context(
            company_id=self.company_id.id, force_company=self.company_id.id
        )._bom_find(product=product_id)
        if bom_id:
            for line in bom_id.bom_line_ids:
                required_qty = needed_qty * line.product_qty
                if line.product_id.virtual_available < required_qty:
                    self.do_make_po(new_procs, line.product_id, -line.product_id.virtual_available)
                    # self.do_make_po(new_procs, line.product_id, required_qty - line.product_id.virtual_available)
        else:
            procs = self.sudo().with_context(non_assign_picking=True).env['procurement.order'].create(self._prepare_proc_order(new_procs,product_id, needed_qty))
            procs.make_po()

    @api.model
    def _prepare_proc_order(self,new_procs,product_id, needed_qty):
        return {
            'name':  new_procs.name or "/",
            'origin': product_id.name,
            'company_id': self.company_id.id,
            'date_planned': self.order_id.confirmation_date,
            'product_id': product_id.id,
            'product_qty': needed_qty,
            'product_uom': product_id.uom_id.id,
            'location_id': new_procs.location_id.id,
            'partner_dest_id': self.order_id.partner_shipping_id.id,
            'move_dest_id': new_procs.move_dest_id.id,
            'group_id': new_procs.group_id.id,
            'route_ids': [(4, x.id) for x in new_procs.route_ids],
            'warehouse_id': new_procs.warehouse_id.id or (new_procs.picking_type_id and new_procs.picking_type_id.warehouse_id.id or False),
            'priority': new_procs.priority,
        }

    def _action_procurement_create(self):
        new_procs = super(SaleOrder, self)._action_procurement_create()
        if new_procs:
            product_id = new_procs.product_id
            rules = product_id.route_ids.mapped('name')
            if 'Buy' in rules and 'Manufacture' in rules:
                MO = self.env['mrp.production']
                root_mo = MO.search(
                    [('product_id', '=', new_procs.product_id.id), ('origin', 'ilike', self.order_id.name)], limit=1)
                if product_id.virtual_available < new_procs.product_qty:
                    if root_mo:
                        # for line in root_mo.move_raw_ids:
                        #     if line.product_id.virtual_available < line.product_uom_qty:
                        needed_qty = new_procs.product_qty - product_id.virtual_available
                        # needed_qty = -product_id.virtual_available
                        self.do_make_po(new_procs, product_id, needed_qty)
                    else:
                        new_procs.product_qty -= product_id.virtual_available
                        new_procs.make_po()