from odoo import fields, models, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from datetime import datetime
import re
import math
from odoo.tools import float_compare, float_round


class lot_number_serializer(models.Model):
    _inherit = 'mrp.production'

    def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        workorders = self.env['mrp.workorder']
        bom_qty = bom_data['qty']
        self.action_assign()

        # Initial qty producing
        if self.product_id.tracking == 'serial':
            quantity = 1.0
        else:
            quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
            quantity = quantity if (quantity > 0) else 0

        for operation in bom.routing_id.operation_ids:
            # create workorder
            cycle_number = math.ceil(bom_qty / operation.workcenter_id.capacity)  # TODO: float_round UP
            duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)

            # Assign Lot/Serial number for Final Product if it have generated before.
            lot_serial_number = self.env['serial.lot.number'].search([('serial_name', '=', self.name)])
            lot_id = False
            if lot_serial_number and lot_serial_number.stock_lot_line_ids:
                stock_lot_line = lot_serial_number.stock_lot_line_ids[0]
                lot_id = self.env['stock.production.lot'].search([('name', '=', stock_lot_line.lot_serial_number)],
                                                                 limit=1)
            workorder = workorders.create({
                'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'operation_id': operation.id,
                'duration_expected': duration_expected,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': quantity,
                'capacity': operation.workcenter_id.capacity,
                'final_lot_id': lot_id.id if lot_id else False
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
            workorders += workorder

            # assign moves; last operation receive all unassigned moves (which case ?)
            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation)
            if len(workorders) == len(bom.routing_id.operation_ids):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
            moves_raw.mapped('move_lot_ids').write({'workorder_id': workorder.id})
            (moves_finished + moves_raw).write({'workorder_id': workorder.id})

            workorder._generate_lot_ids()
        return workorders

    def print_product_lot(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'warehouse_serializer_mrp.qrcode_label',
            'report_type': 'qweb-pdf',
        }

    def generate_qr_code(self):
        data = []
        now = datetime.now()
        user_tz = self.env.user.tz or 'Singapore'
        local = pytz.timezone(user_tz)
        now = pytz.utc.localize(now).astimezone(local).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for finish in self.move_finished_ids:
            for move_lot in finish.active_move_lot_ids:
                if finish.product_id and finish.product_id.barcode:
                    code = finish.product_id.barcode + ',' + move_lot.lot_id.name + ','
                else:
                    code = move_lot.lot_id.name + ','

                if move_lot.lot_id and move_lot.lot_id.use_date:
                    code += str(move_lot.lot_id.use_date)[0:10]
                data.append({
                    'code'   : str(re.escape(code)),
                    'product': finish.product_id.name,
                    'barcode': finish.product_id.barcode if finish.product_id.barcode else '',
                    'lot'    : move_lot.lot_id.name,
                    'expiry_date': move_lot.lot_id.use_date,
                    'date' : now
                })
        return data

    def action_product_to_serializer_mrp(self):
        vals_create = {}
        stock_product_id = self.env['serial.lot.number'].search([('serial_name','=', self.name)])
        view_ref = self.env['ir.model.data'].get_object_reference('warehouse_serializer_mrp', 'view_form_serial_lot_from_mo')
        view_id = view_ref[1] if view_ref else False
        if not stock_product_id:
            stock_lot_number = ''
            for product in self.move_finished_ids:

                if (product.product_uom_qty == 1.00):
                    check_lot_number = True
                else:
                    check_lot_number = False

                vals_create.update({'serial_name': self.name})

                if stock_lot_number:
                    stock_lot_number.write(vals_create)

                    if product.product_id.tracking == 'serial':
                        for qty in range(int(product.product_uom_qty)):
                            stock_lot_number.write({'stock_lot_line_ids': [
                                (0, 0, {'product_id': product.product_id.id,
                                        'quantity': product.quantity_done,
                                        'location_id': product.location_id.id,
                                        'check_lot_number': check_lot_number,
                                        'main_product': True,
                                        'source_location_id': product.location_dest_id.id,
                                        'location_dest_id': product.location_dest_id.id,
                                        })]})
                    elif product.product_id.tracking == 'lot':
                        stock_lot_number.write({'stock_lot_line_ids': [
                            (0, 0, {'product_id': product.product_id.id,
                                    'quantity': product.quantity_done,
                                    'location_id': product.location_id.id,
                                    'check_lot_number': check_lot_number,
                                    'main_product': True,
                                    'source_location_id': product.location_dest_id.id,
                                    'location_dest_id': product.location_dest_id.id,
                                    })]})

                else:
                    stock_lot_number = self.env['serial.lot.number'].create(vals_create)
                    if product.product_id.tracking == 'serial':
                        for qty in range(int(product.product_uom_qty)):
                            stock_lot_number.write({'stock_lot_line_ids': [
                                (0, 0, {'product_id': product.product_id.id,
                                        'quantity': product.quantity_done,
                                        'location_id': product.location_id.id,
                                        'check_lot_number': check_lot_number,
                                        'main_product': True,
                                        'source_location_id': product.location_dest_id.id,
                                        'location_dest_id': product.location_dest_id.id,
                                        })]})
                    elif product.product_id.tracking == 'lot':
                        stock_lot_number.write({'stock_lot_line_ids': [
                            (0, 0, {'product_id': product.product_id.id,
                                    'quantity': product.quantity_done,
                                    'location_id': product.location_id.id,
                                    'check_lot_number': check_lot_number,
                                    'main_product': True,
                                    'source_location_id': product.location_dest_id.id,
                                    'location_dest_id': product.location_dest_id.id,
                                    })]})
            #stock_product_id.split_quantities()
            for line in stock_lot_number.stock_lot_line_ids:
                line.generate_lot_number_mrp()


            res = {
                'type': 'ir.actions.act_window',
                'name': _('Customer Serial Number'),
                'res_model': 'serial.lot.number',
                'res_id': stock_lot_number.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'new',

            }
        else :

            #stock_product_id.split_quantities()
            for line in stock_product_id.stock_lot_line_ids:
                line.generate_lot_number_mrp()
            res = {
                'type': 'ir.actions.act_window',
                'name': _('Customer Serial Number'),
                'res_model': 'serial.lot.number',
                'res_id': stock_product_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'new',

            }
        return res

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _generate_lot_ids(self):
        """ Generate stock move lots """
        self.ensure_one()
        MoveLot = self.env['stock.move.lots']
        tracked_moves = self.move_raw_ids.filtered(
            lambda move: move.state not in ('done', 'cancel') and move.product_id.tracking != 'none' and move.product_id != self.production_id.product_id)
        for move in tracked_moves:
            qty = move.unit_factor * self.qty_producing
            if move.product_id.tracking == 'serial':
                while float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                    MoveLot.create({
                        'move_id': move.id,
                        'quantity': min(1, qty),
                        'quantity_done': min(1, qty),
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                    })
                    qty -= 1
            else:
                # Follow move_lot_ids.
                for move_lot in move.move_lot_ids:
                    MoveLot.create({
                        'lot_id' : move_lot.lot_id.id,
                        'move_id': move.id,
                        'quantity': move_lot.quantity,
                        'quantity_done': move_lot.quantity,
                        'product_id': move.product_id.id,
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'done_wo': False,
                        })

class ProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def default_get(self, fields):
        res = super(ProductProduce, self).default_get(fields)
        ctx = self._context
        model = ctx.get('active_model')
        active_id = ctx.get('active_id')
        if model and active_id:
            production_id = self.env[model].browse(active_id)
            lot_number_serializer = self.env['serial.lot.number'].search([('serial_name','=', production_id.name)], limit=1)
            if lot_number_serializer:
                lot_product = lot_number_serializer.stock_lot_line_ids.filtered(lambda x:x.product_id == production_id.product_id)
                if lot_product:
                    stock_production_lot = self.env['stock.production.lot'].search([('name', '=', lot_product[0].lot_serial_number)])
                    if stock_production_lot:
                        res['lot_id'] = stock_production_lot.id
        return res

