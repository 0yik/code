from odoo import models, fields, api


class stock_picking(models.Model):
    _inherit = 'stock.picking'

    code = fields.Selection([('incoming','Vendors'), ('outgoing','Delivery Orders'), ('internal','Internal')],
                            'Type of Operation', related="picking_type_id.code", store=True)
