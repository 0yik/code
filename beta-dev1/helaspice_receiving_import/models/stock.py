from odoo import models, fields, api
from odoo.tools.float_utils import float_compare

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipment_id = fields.Many2one('shipment.reference', readonly=True, string='Shipment')
    pallet_no = fields.Integer(readonly=True, string='Pallet No')
    po_reference = fields.Char(readonly=True, string='PO Reference')

    def get_waiting_availability(self):
        self.ensure_one()
        data_list = []
        location_id = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_stock')
        for move_id in self.move_lines:
            vals = {}
            product_id = move_id.product_id
            vals['move_id'] = move_id.id
            vals['product_id'] = product_id.id
            vals['product'] = product_id.name
            vals['barcode'] = product_id.barcode
            vals['item_no'] = product_id.default_code
            vals['rack_location'] = product_id.rack_location
            vals['qty'] = move_id.product_uom_qty
            if product_id.tracking == 'none':
                vals['tracking'] = 'N'
            else:
                vals['tracking'] = 'Y'
            if self.state in ['partially_available', 'assigned']:
                quants_dict = {}
                scanned_qty = 0
                quant_list = []
                for quant in self.env['stock.quant'].search([('location_id', '=', location_id), ('product_id', '=', product_id.id), ('lot_id', '!=', False), ('reservation_id', '=', move_id.id)]):
                    lot_id = quant.lot_id
                    if lot_id.id in quants_dict:
                        quants_dict[lot_id.id]['scanned_qty'] += quant.qty
                    else:
                        quant_vals = {}
                        quant_vals['lot_name'] = lot_id.name
                        quant_vals['lot_id'] = lot_id.id
                        quant_vals['batch_no'] = lot_id.batch_no if not lot_id.actual_batch_no else lot_id.actual_batch_no
                        quant_vals['scanned_qty'] = quant.qty
                        if lot_id.actual_bbd:
                            quant_vals['bbd'] = str(lot_id.actual_bbd)[:10]
                        else:
                            quant_vals['bbd'] = str(lot_id.use_date)[:10] if lot_id.use_date else ''
                        quants_dict[lot_id.id] = quant_vals
                for key in quants_dict.keys():
                    scanned_qty += quants_dict[key]['scanned_qty']
                    quant_list.append(quants_dict[key])
                if product_id.tracking == 'none':
                    scanned_qty = move_id.reserved_availability
                vals['total_scanned_qty'] = scanned_qty
                vals['scanned_data'] = quant_list
            data_list.append(vals)
        return data_list

    # For the app
    # Get Picking data for the single IN
    def get_picking_data(self):
        self.ensure_one()
        data_list = []
        for pack_id in self.pack_operation_product_ids:
            vals = {}
            product_id = pack_id.product_id
            vals['pack_id'] = pack_id.id
            vals['product_id'] = product_id.id
            vals['rack_location'] = product_id.rack_location
            vals['product'] = product_id.name
            vals['barcode'] = product_id.barcode
            vals['item_no'] = product_id.default_code
            vals['qty'] = pack_id.product_qty
            if product_id.tracking == 'none':
                vals['tracking'] = 'N'
            else:
                vals['tracking'] = 'Y'
            if self.picking_type_code == 'incoming':
                tracking_list = []
                tracking_dict = {}
                for receiving_batch in self.env['manage.incoming.batch'].search([('product_id', '=', product_id.id), ('picking_ids', 'in', self.id)]):
                    qty = receiving_batch.qty - receiving_batch.done_qty
                    if receiving_batch.lot_id.id in tracking_dict:
                        if qty > 0:
                            tracking_dict[receiving_batch.lot_id.id]['qty'] += qty
                    else:
                        lot_vals = {}
                        lot_vals['lot_id'] = receiving_batch.lot_id.id
                        lot_vals['lot_name'] = receiving_batch.lot_id.name
                        lot_vals['batch_no'] = receiving_batch.batch_no
                        lot_vals['bbd'] = str(receiving_batch.use_date)[:10] if receiving_batch.use_date else ''
                        if qty > 0:
                            lot_vals['qty'] = qty
                        else:
                            lot_vals['qty'] = 0
                        tracking_dict[receiving_batch.lot_id.id] = lot_vals
                for key in tracking_dict.keys():
                    tracking_list.append(tracking_dict[key])
                vals['tracking_data'] = tracking_list
            data_list.append(vals)
        return data_list

    def app_action_assign(self, data_list):
        if self.state not in ['confirmed', 'partially_available', 'assigned']:
            return False
        self.do_unreserve()
        self.with_context(picking_reserve=data_list).action_assign()
        return True

    # For the app
    # Once the scanning process done. Call this method to move the IN to done state
    def app_action_done(self, data_list):
        self.ensure_one()
        if self.state not in ['partially_available', 'assigned']:
            return False
        try:
            for data_dict in data_list:
                pack_id = self.pack_operation_product_ids.filtered(lambda x: x.id == data_dict.get('pack_id', False))
                if pack_id:
                    pack_lot_list = []
                    for lot_dict in data_dict.get('scanned_data', []):
                        vals = {}
                        lot_id = self.env['stock.production.lot'].search([('product_id', '=', pack_id.product_id.id), ('name', '=', lot_dict.get('lot_name', ''))], limit=1)
                        if not lot_id:
                            lot_id = self.env['stock.production.lot'].create({'name': lot_dict.get('lot_name', ''), 'product_id': pack_id.product_id.id})
                        vals['lot_name'] = lot_dict.get('lot_name', '')
                        vals['lot_id'] = lot_id.id
                        vals['qty'] = lot_dict.get('qty')
                        pack_lot_list.append((0, 0, vals))
                    pack_id.pack_lot_ids.unlink()
                    pack_id.write({'pack_lot_ids': pack_lot_list, 'qty_done': data_dict.get('qty', 0)})
            transfer_dict = self.sudo().do_new_transfer()
            if type(transfer_dict) == dict and transfer_dict.get('res_model') and transfer_dict.get('res_id'):
                wiz_obj = self.env[transfer_dict['res_model']].sudo().browse(transfer_dict['res_id'])
                wiz_obj.process()
            return True
        except:
            return False

    # Partial Receiving Import
    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        backorders = super(StockPicking, self)._create_backorder(backorder_moves)
        for backorder in backorders.filtered(lambda x: x.picking_type_code == 'incoming'):
            vals = {}
            vals['shipment_id'] = backorder.backorder_id.shipment_id.id if backorder.backorder_id.shipment_id else False
            vals['pallet_no'] = backorder.backorder_id.pallet_no
            vals['po_reference'] = backorder.backorder_id.po_reference
            backorder.write(vals)
            for incoming_batch in self.env['manage.incoming.batch'].search([('picking_ids', 'in', backorder.backorder_id.id)]):
                if incoming_batch.product_id.id in [x.product_id.id for x in backorder.pack_operation_product_ids]:
                    incoming_batch.write({'picking_ids': [(4, backorder.id)]})
        for backorder in backorders.filtered(lambda x: x.picking_type_code == 'outgoing' and x.state in ['partially_available', 'assigned']):
            backorder.do_unreserve()
        return backorders

    def log_a_note(self, note):
        self.ensure_one()
        if note.strip():
            self.write({'note': note.strip()})
            self.message_post('<b>Remarks:</b><ul><li>%s.</li></ul>'% note.strip())
        else:
            self.write({'note': False})
        return True

StockPicking()

class StockMove(models.Model):
    _inherit = 'stock.move'

    po_ref = fields.Char('PO Reference')
    sap_ref = fields.Char('SAP Reference')

    def get_unreserved_quants(self):
        if not self:
            return []
        self.ensure_one()
        quants_dict = {}
        location_id = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_stock')
        domain = [('location_id', '=', location_id), ('product_id', '=', self.product_id.id), ('lot_id', '!=', False)]
        quants = self.env['stock.quant'].search(domain + [('reservation_id', '=', False)])
        quants += self.env['stock.quant'].search(domain + [('reservation_id', '=', self.id)])
        for quant in quants:
            lot_id = quant.lot_id
            if lot_id.id in quants_dict:
                if quant.reservation_id:
                    quants_dict[lot_id.id]['scanned_qty'] += quant.qty
                    quants_dict[lot_id.id]['qty'] += quant.qty
                else:
                    quants_dict[lot_id.id]['qty'] += quant.qty
            else:
                vals = {}
                vals['lot_name'] = lot_id.name
                vals['lot_id'] = lot_id.id
                vals['batch_no'] = lot_id.batch_no if not lot_id.actual_batch_no else lot_id.actual_batch_no
                vals['qty'] = quant.qty
                vals['scanned_qty'] = 0
                if quant.reservation_id:
                    vals['scanned_qty'] = quant.qty
                if lot_id.actual_bbd:
                    vals['bbd'] = str(lot_id.actual_bbd)[:10]
                else:
                    vals['bbd'] = str(lot_id.use_date)[:10] if lot_id.use_date else ''
                quants_dict[lot_id.id] = vals
        quant_list = []
        for key in quants_dict.keys():
            quant_list.append(quants_dict[key])
        return quant_list

    @api.multi
    def action_assign(self, no_prepare=False):
        ctx = self._context or {}
        if not ctx.get('picking_reserve', False):
            return super(StockMove, self).action_assign(no_prepare=no_prepare)

        main_domain = {}
        Quant = self.env['stock.quant']
        Uom = self.env['product.uom']
        moves_to_assign = self.env['stock.move']
        moves_to_do = self.env['stock.move']
        operations = self.env['stock.pack.operation']
        ancestors_list = {}

        # work only on in progress moves
        moves = self.filtered(lambda move: move.state in ['confirmed', 'waiting', 'assigned'])
        moves.filtered(lambda move: move.reserved_quant_ids).do_unreserve()
        for move in moves:
            if move.location_id.usage in ('supplier', 'inventory', 'production'):
                moves_to_assign |= move
                # in case the move is returned, we want to try to find quants before forcing the assignment
                if not move.origin_returned_move_id:
                    continue
            # if the move is preceeded, restrict the choice of quants in the ones moved previously in original move
            ancestors = move.find_move_ancestors()
            if move.product_id.type == 'consu' and not ancestors:
                moves_to_assign |= move
                continue
            else:
                moves_to_do |= move

                # we always search for yet unassigned quants
                main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]

                ancestors_list[move.id] = True if ancestors else False
                if move.state == 'waiting' and not ancestors:
                    # if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't find any quant available in stock
                    main_domain[move.id] += [('id', '=', False)]
                elif ancestors:
                    main_domain[move.id] += [('history_ids', 'in', ancestors.ids)]

                # if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
                if move.origin_returned_move_id:
                    main_domain[move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
                for link in move.linked_move_operation_ids:
                    operations |= link.operation_id

        # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
        operations = operations.sorted(
            key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (
                    x.pack_lot_ids and -1 or 0))
        for ops in operations:
            # first try to find quants based on specific domains given by linked operations for the case where we want to rereserve according to existing pack operations
            if not (ops.product_id and ops.pack_lot_ids):
                for record in ops.linked_move_operation_ids:
                    move = record.move_id
                    if move.id in main_domain:
                        qty = record.qty
                        domain = main_domain[move.id]
                        if qty:
                            quants = Quant.quants_get_preferred_domain(qty, move, ops=ops, domain=domain, preferred_domain_list=[])
                            Quant.quants_reserve(quants, move, record)
            else:
                lot_qty = {}
                rounding = ops.product_id.uom_id.rounding
                for pack_lot in ops.pack_lot_ids:
                    lot_qty[pack_lot.lot_id.id] = ops.product_uom_id._compute_quantity(pack_lot.qty,
                                                                                       ops.product_id.uom_id)
                for record in ops.linked_move_operation_ids:
                    move_qty = record.qty
                    move = record.move_id
                    domain = main_domain[move.id]
                    for lot in lot_qty:
                        if float_compare(lot_qty[lot], 0, precision_rounding=rounding) > 0 and float_compare(move_qty, 0, precision_rounding=rounding) > 0:
                            qty = min(lot_qty[lot], move_qty)
                            quants = Quant.quants_get_preferred_domain(qty, move, ops=ops, lot_id=lot, domain=domain, preferred_domain_list=[])
                            Quant.quants_reserve(quants, move, record)
                            lot_qty[lot] -= qty
                            move_qty -= qty

        # Sort moves to reserve first the ones with ancestors, in case the same product is listed in
        # different stock moves.
        data_list = ctx.get('picking_reserve', [])
        for move in sorted(moves_to_do, key=lambda x: -1 if ancestors_list.get(x.id) else 0):
            # then if the move isn't totally assigned, try to find quants without any specific domain
            if move.state != 'assigned' and not self.env.context.get('reserve_only_ops'):
                # qty_already_assigned = move.reserved_availability
                # qty = move.product_qty - qty_already_assigned
                for data_dict in data_list:
                    if data_dict.get('move_id', False) == move.id:
                        if move.product_id.tracking == 'none':
                            quants = Quant.quants_get_preferred_domain(data_dict.get('qty', 0), move, domain=main_domain[move.id], preferred_domain_list=[])
                            Quant.quants_reserve(quants, move)
                        else:
                            for lot_dict in data_dict.get('scanned_data', []):
                                if lot_dict['qty'] > 0:
                                    lot_id = self.env['stock.production.lot'].search([('name', '=', lot_dict['lot_name']), ('product_id', '=', move.product_id.id)])
                                    if lot_id:
                                        quants = Quant.quants_get_preferred_domain(lot_dict['qty'], move, domain=main_domain[move.id] + [('lot_id', '=', lot_id.id)], preferred_domain_list=[])
                                        Quant.quants_reserve(quants, move)
        # force assignation of consumable products and incoming from supplier/inventory/production
        # Do not take force_assign as it would create pack operations
        if moves_to_assign:
            moves_to_assign.write({'state': 'assigned'})
        if not no_prepare:
            self.check_recompute_pack_op()

StockMove()