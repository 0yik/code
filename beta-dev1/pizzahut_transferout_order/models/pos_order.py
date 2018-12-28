# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json 


class PosOrder(models.Model):
    _inherit= "pos.order"

    source_branch = fields.Many2one('res.branch', string="Source Branch")
    destination_branch = fields.Many2one('res.branch',string="Destination Branch")
    transfer_order_address = fields.Text('Address')
    is_transfer_out = fields.Boolean(string="Is transfer out?", default=False)
    is_order_proceed = fields.Boolean(string="Is order proceed?", default=False)
    bus_id = fields.Many2one(related='session_id.config_id.bus_id',string="bus")
    export_as_JSON_data = fields.Text(string="Order JSON data")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        print "----------------ui_order ---------------------------"
        print ui_order
        print "----------------ui_order ---------------------------"

        source_branch = None
        if ui_order.get('pos_session_id'):
            pos_session_id = self.env['pos.session'].browse(ui_order.get('pos_session_id'))
            source_branch = pos_session_id.config_id.branch_id.id
        res['source_branch'] = source_branch
        res['destination_branch'] = ui_order.get('transfer_branch_id')
        res['transfer_order_address'] = ui_order.get('transfer_address')
        res['is_transfer_out'] = ui_order.get('is_transfer_out')
        # if ui_order.get('statement_ids'):
        #     ui_order['statement_ids'] = []
        res['export_as_JSON_data'] = json.dumps(ui_order)
        return res

# class res_branch(models.Model):
#     _inherit = 'res.branch'
#     _rec_name = 'name'
