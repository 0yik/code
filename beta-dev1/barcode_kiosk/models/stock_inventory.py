# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
date = datetime.strptime(fields.Date.today(), '%Y-%m-%d').strftime('%y')


class StockInventory(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def open_stock_out_picking(self, emp_id):
        emp = self.env['hr.employee'].browse(emp_id)
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)],
                                                                  limit=1)
        outgoing_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'outgoing')], limit=1)
        out_location_dest_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
        physical_location_id = self.env['ir.model.data'].get_object_reference('stock','stock_location_locations')
        wh_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', physical_location_id and physical_location_id[1]),
                        ('usage', '=', 'view')], limit=1)
        stock_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', wh_location_id and wh_location_id.id),
                        ('usage', '=', 'internal')], limit=1)
        action = self.env.ref('barcode_kiosk.stock_inventory_action_out_picking').read()[0]
        seq = self.env['ir.sequence'].next_by_code('stock.picking.barcode.out')
        if emp_id:
            new_inv = self.env['stock.picking'].create({
                    'name': 'SO-'+ date + seq,
                    'partner_id': emp.user_id and emp.user_id.partner_id.id or False,
                    'picking_type_id': outgoing_type_id.id or False,
                    'location_id': stock_location_id and stock_location_id.id or False,
                    'location_dest_id': out_location_dest_id and out_location_dest_id.id or False,
                    'state': 'assigned',
            })
            action['res_id'] = new_inv.id
            return action

    @api.model
    def open_stock_in_picking(self, emp_id):
        emp = self.env['hr.employee'].browse(emp_id)
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)],
                                                                  limit=1)
        incoming_type_id = self.env['stock.picking.type'].search(
                        [('warehouse_id', '=', warehouse_id[0].id), ('code', '=', 'incoming')], limit=1)
        in_location_id = self.env['stock.location'].search(
                        [('usage', '=', 'supplier')], limit=1)
        physical_location_id = self.env['ir.model.data'].get_object_reference('stock','stock_location_locations')
        wh_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', physical_location_id and physical_location_id[1]),
                        ('usage', '=', 'view')], limit=1)
        stock_location_id = self.env['stock.location'].search(
                        [('company_id', '=', user_obj.company_id.id),
                        ('location_id', '=', wh_location_id and wh_location_id.id),
                        ('usage', '=', 'internal')], limit=1)
        action = self.env.ref('barcode_kiosk.stock_inventory_action_in_picking').read()[0]
        seq = self.env['ir.sequence'].next_by_code('stock.picking.barcode.in')
        if emp_id:
            new_inv = self.env['stock.picking'].create({
                    'name': 'SI'+ date + '-' + seq,
                    'partner_id': emp.user_id and emp.user_id.partner_id.id or False,
                    'picking_type_id': incoming_type_id.id or False,
                    'location_id': in_location_id and in_location_id.id or False,
                    'location_dest_id': stock_location_id and stock_location_id.id or False,
                    'state': 'assigned',
            })
            action['res_id'] = new_inv.id
            return action


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def open_new_inventory(self):
        action = self.env.ref('barcode_kiosk.stock_inventory_action_new_inventory').read()[0]
        if self.env.ref('stock.warehouse0', raise_if_not_found=False):
            new_inv = self.env['stock.inventory'].create({
                'filter': 'partial',
                'name': 'ST'+ date + '-' + self.env['ir.sequence'].next_by_code('stock.picking.barcode'),
            })
            new_inv.prepare_inventory()
            action['res_id'] = new_inv.id
        return action
