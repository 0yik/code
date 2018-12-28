import math
from odoo import models, fields, api
from odoo.tools import float_compare, float_round

class quantity_mrp_routing_workcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    quantity_range_start = fields.Float(required = True)
    quantity_range_end = fields.Float(required = True)
    routing_oum = fields.Many2one('product.uom',string='UOM', required = True)



class select_workcenter(models.Model):
    _inherit='mrp.production'

    # @api.model
    # def create(self,vals):
    #     res = super(select_workcenter, self).create(vals)
    #     res.button_plan()
    #     product_lines = res.move_raw_ids
    #     routing_id = res.routing_id
    #     if routing_id:
    #         workcenter_lines = routing_id.operation_ids
    #         for line in product_lines:
    #             for workcenter_line in workcenter_lines:
    #                 if workcenter_line.quantity_range_start and workcenter_line.quantity_range_end and workcenter_line.routing_oum:
    #                     if line.product_uom.id == workcenter_line.routing_oum.id:
    #                         if line.product_qty >= workcenter_line.quantity_range_start and line.product_qty <= workcenter_line.quantity_range_end:
    #                             workorders = self.env['mrp.workorder'].search([('production_id','=',res.id)])
    #                             for workorder in workorders:
    #                                 if workorder.workcenter_id.id == workcenter_line.workcenter_id.id:
    #                                     workorder.button_start()
    #                             break
    #     return res


    # TODO: Override create Work Oder based on Production
    def _workorders_create(self, bom, bom_data):
        """
        :param bom: in case of recursive boms: we could create work orders for child
                    BoMs
        """
        workorders = self.env['mrp.workorder']
        bom_qty = bom_data['qty']

        # Initial qty producing
        if self.product_id.tracking == 'serial':
            quantity = 1.0
        else:
            quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
            quantity = quantity if (quantity > 0) else 0

        for operation in bom.routing_id.operation_ids:
            ids = []
            for move in self.move_raw_ids:
                if move.product_qty >= operation.quantity_range_start and move.product_qty <= operation.quantity_range_end:
                    ids.append(move.id)
            if ids:
                # create workorder
                cycle_number = math.ceil(bom_qty / operation.workcenter_id.capacity)  # TODO: float_round UP
                duration_expected = (operation.workcenter_id.time_start +
                                     operation.workcenter_id.time_stop +
                                     cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
                workorder = workorders.create({
                    'name': operation.name,
                    'production_id': self.id,
                    'workcenter_id': operation.workcenter_id.id,
                    'operation_id': operation.id,
                    'duration_expected': duration_expected,
                    'state': len(workorders) == 0 and 'ready' or 'pending',
                    'qty_producing': quantity,
                    'capacity': operation.workcenter_id.capacity,
                    'move_raw_ids' : [(6,0,ids)],
                })
                if workorders:
                    workorders[-1].next_work_order_id = workorder.id
                workorders += workorder
                workorder._generate_lot_ids()
        return workorders

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    # TODO: Override generate active move lot.
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
                        # 'quantity_done': min(1, qty),
                        'quantity_done': 0,
                        'production_id': self.production_id.id,
                        'workorder_id': self.id,
                        'product_id': move.product_id.id,
                        'done_wo': False,
                    })
                    qty -= 1
            else:
                MoveLot.create({
                    'move_id': move.id,
                    'quantity': qty,
                    # 'quantity_done': qty,
                    'quantity_done': 0,
                    'product_id': move.product_id.id,
                    'production_id': self.production_id.id,
                    'workorder_id': self.id,
                    'done_wo': False,
                    })
        self.arrange_bom()

    def arrange_bom(self):
        if self.active_move_lot_ids:
            i = 1
            product_not_volatiles = self.active_move_lot_ids.filtered(lambda line: line.product_id.product_tmpl_id.volatile == False)
            product_volatiles = self.active_move_lot_ids.filtered(lambda line: line.product_id.product_tmpl_id.volatile == True)
            product_powders = product_not_volatiles.filtered(lambda line: line.product_id.product_tmpl_id.form == 'powder')
            product_powders = sorted(product_powders, key=lambda product: product.quantity, reverse=True)
            product_liquiqs = product_not_volatiles.filtered(lambda line: line.product_id.product_tmpl_id.form == 'liquiq')
            product_liquiqs = sorted(product_liquiqs, key=lambda product: product.quantity, reverse=True)
            for product in product_powders:
                product.sequence = i
                i += 1
            for product in product_liquiqs:
                product.sequence = i
                i += 1
            for product in product_volatiles:
                product.sequence = i
                i += 1

