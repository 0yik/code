from odoo import models, fields, api
from datetime import datetime

class quantity_mrp_routing_workcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    quantity_range_start = fields.Float(required = True)
    quantity_range_end = fields.Float(required = True)
    routing_oum = fields.Many2one('product.uom',string='UOM', required = True)



class select_workcenter(models.Model):
    _inherit='mrp.production'

    @api.model
    def create(self,vals):
        res = super(select_workcenter, self).create(vals)
        res.button_plan()
        product_lines = res.move_raw_ids
        routing_id = res.routing_id
        if routing_id:
            workcenter_lines = routing_id.operation_ids
            for line in product_lines:
                for workcenter_line in workcenter_lines:
                    if workcenter_line.quantity_range_start and workcenter_line.quantity_range_end and workcenter_line.routing_oum:
                        if line.product_uom.id == workcenter_line.routing_oum.id:
                            if line.product_qty >= workcenter_line.quantity_range_start and line.product_qty <= workcenter_line.quantity_range_end:
                                workorders = self.env['mrp.workorder'].search([('production_id','=',res.id)])
                                for workorder in workorders:
                                    if workorder.workcenter_id.id == workcenter_line.workcenter_id.id:
                                        workorder.button_start()
                                break
        return res

