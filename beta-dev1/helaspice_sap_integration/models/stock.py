from odoo import models, fields, api
import requests
import json
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sap_pick_number = fields.Integer()

    def create_picklist(self, pick_dict):
        try:
            if not pick_dict.get('Lines', []):
                return 0
            picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
            location_id = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_stock')
            location_dest_id = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_customers')
            vals = {}
            vals['picking_type_id'] = picking_type_id.id
            vals['location_id'] = location_id
            vals['location_dest_id'] = location_dest_id
            vals['sap_pick_number'] = int(pick_dict.get('PickNumber', 0))
            vals['note'] = pick_dict.get('Remarks', False)
            picking_id = self.env['stock.picking'].create(vals)
            for line_dict in pick_dict.get('Lines', []):
                move_vals = {}
                move_vals['picking_id'] = picking_id.id
                product_id = False
                if line_dict.get('ItemCode', False):
                    product_id = self.env['product.product'].search([('default_code', '=', line_dict['ItemCode'])], limit=1)
                if not product_id and line_dict.get('Description', False):
                    product_id = self.env['product.product'].search([('name', '=', line_dict['Description']), ('default_code', '=', False)], limit=1)
                    if product_id:
                        product_id.write({'default_code': line_dict.get('ItemCode', '')})
                    else:
                        product_vals = {}
                        product_vals['name'] = line_dict.get('Description', False)
                        product_vals['default_code'] = line_dict.get('ItemCode', False)
                        product_vals['barcode'] = line_dict.get('ItemBarcode', False)
                        product_vals['type'] = 'product'
                        product_vals['rack_location'] = line_dict.get('RackLocation', False)
                        if line_dict.get('IsSerial', 'N') == 'Y':
                            product_vals['tracking'] = 'serial'
                        elif line_dict.get('IsBatch', 'N') == 'Y':
                            product_vals['tracking'] = 'lot'
                        product_id = self.env['product.product'].create(product_vals)
                if product_id and float(line_dict.get('AvailQty', 0)):
                    move_vals['product_id'] = product_id.id
                    move_vals['name'] = product_id.name
                    move_vals['product_uom_qty'] = float(line_dict.get('AvailQty', 0))
                    move_vals['product_uom'] = product_id.uom_id.id if product_id.uom_id else False
                    move_vals['location_id'] = location_id
                    move_vals['location_dest_id'] = location_dest_id
                    move_vals['po_ref'] = line_dict.get('POREF', '')
                    move_vals['sap_ref'] = line_dict.get('SAPREF', '')
                    move_vals['sap_order_entry'] = int(line_dict.get('OrderEntry', 0))
                    move_vals['sap_line_number'] = int(line_dict.get('LineNumber', 0))
                    move_vals['sap_order_line_number'] = int(line_dict.get('OrderLineNumber', 0))
                    self.env['stock.move'].create(move_vals)
            picking_id.action_confirm()
            return picking_id.id
        except:
            return 0

    def push_picklist(self):
        url = self.env['ir.config_parameter'].get_param('sap.url', default=None)
        username = self.env['ir.config_parameter'].get_param('sap.username', default=None)
        password = self.env['ir.config_parameter'].get_param('sap.password', default=None)
        if not url or not username or not password:
            raise UserError('Invalid configuration for SAP.')
        vals = {}
        vals['PickNumber'] = self.sap_pick_number
        vals['Remarks'] = self.note
        line_list = []
        for line in self.move_lines:
            line_vals = {}
            line_vals['PickNumber'] = self.sap_pick_number
            line_vals['OrderEntry'] = line.sap_order_entry
            line_vals['LineNumber'] = line.sap_line_number
            line_vals['OrderLineNumber'] = line.sap_order_line_number
            line_vals['ItemCode'] = line.product_id.default_code
            line_vals['AvailQty'] = line.product_uom_qty
            if line.product_id.tracking == 'serial':
                line_vals['IsBatch'] = 'N'
                line_vals['IsSerial'] = 'Y'
            elif line.product_id.tracking == 'lot':
                line_vals['IsBatch'] = 'Y'
                line_vals['IsSerial'] = 'N'
            else:
                line_vals['IsBatch'] = 'N'
                line_vals['IsSerial'] = 'N'
            serial_list = []
            batch_list = []
            if line.reserved_quant_ids:
                lot_dict = {}
                if line_vals['IsSerial'] == 'Y':
                    for quant in line.reserved_quant_ids:
                        lot_id = quant.lot_id
                        if lot_id.name in lot_dict:
                            lot_dict[lot_id.name]['Quantity'] += quant.qty
                        else:
                            lot_vals = {}
                            lot_vals['PickNumber'] = self.sap_pick_number
                            lot_vals['OrderEntry'] = line.sap_order_entry
                            lot_vals['LineNumber'] = line.sap_line_number
                            lot_vals['SerialNumber'] = lot_id.display_batch_no
                            lot_vals['Quantity'] = quant.qty
                            lot_vals['ExpiryDate'] = lot_id.display_bbd[:10] if lot_id.display_bbd else ''
                            lot_dict[lot_id.name] = lot_vals
                    for l in lot_dict.keys():
                        serial_list.append(lot_dict[l])
                elif line_vals['IsBatch'] == 'Y':
                    for quant in line.reserved_quant_ids:
                        lot_id = quant.lot_id
                        if lot_id.name in lot_dict:
                            lot_dict[lot_id.name]['Quantity'] += quant.qty
                        else:
                            lot_vals = {}
                            lot_vals['PickNumber'] = self.sap_pick_number
                            lot_vals['OrderEntry'] = line.sap_order_entry
                            lot_vals['LineNumber'] = line.sap_line_number
                            lot_vals['BatchNumber'] = lot_id.display_batch_no
                            lot_vals['ExpiryDate'] = lot_id.display_bbd[:10] if lot_id.display_bbd else ''
                            lot_vals['Quantity'] = quant.qty
                            lot_dict[lot_id.name] = lot_vals
                    for l in lot_dict.keys():
                        batch_list.append(lot_dict[l])
            line_vals['PickQty'] = line.reserved_availability
            line_vals['Serial'] = serial_list
            line_vals['Batch'] = batch_list
            line_list.append(line_vals)
        vals['Lines'] = line_list
        try:
            url += '/POST_PICKLIST'
            headers = {'content-type': 'application/json'}
            request = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(vals))
            response = request.json()
            self.message_post(response)
        except:
            raise UserError('Invalid Configuration')

    def action_delivery(self, line_list):
        self.ensure_one()
        try:
            for line_dict in line_list:
                if line_dict.get('ItemCode', False):
                    product_id = self.env['product.product'].search([('default_code', '=', line_dict.get('ItemCode'))], limit=1)
                    if product_id:
                        pack = self.pack_operation_product_ids.filtered(lambda x: x.product_id.id == product_id.id)
                        if pack:
                            if product_id.tracking == 'none':
                                pack.write({'qty_done': line_dict.get('PickQty', 0)})
                            elif product_id.tracking == 'lot':
                                for lot_dict in line_dict.get('Batch', []):
                                    pack_lot = pack.pack_lot_ids.filtered(lambda x: x.lot_id.display_batch_no == str(lot_dict.get('BatchNumber', '')))
                                    if pack_lot:
                                        pack_lot.write({'qty': lot_dict.get('Quantity', 0)})
                                pack._onchange_packlots()
                            else:
                                for lot_dict in line_dict.get('Serial', []):
                                    pack_lot = pack.pack_lot_ids.filtered(lambda x: x.lot_id.display_batch_no == str(lot_dict.get('SerialNumber', '')))
                                    if pack_lot:
                                        pack_lot.write({'qty': lot_dict.get('Quantity', 0)})
                                pack._onchange_packlots()
            transfer_dict = self.sudo().do_new_transfer()
            if type(transfer_dict) == dict and transfer_dict.get('res_model') and transfer_dict.get('res_id'):
                wiz_obj = self.env[transfer_dict['res_model']].sudo().browse(transfer_dict['res_id'])
                wiz_obj.process()
            backorder = self.search([('backorder_id', '=', self.id)], order='id desc', limit=1)
            if backorder:
                return backorder.id
            else:
                return self.id
        except:
            return 0

    def action_picked_delivery(self):
        self.ensure_one()
        try:
            for pack in self.pack_operation_product_ids:
                if pack.product_id.tracking == 'none':
                    pack.write({'qty_done': pack.product_qty})
                else:
                    for pack_lot in pack.pack_lot_ids:
                        pack_lot.write({'qty': pack_lot.qty_todo})
                        # for i in range(0, int(pack_lot.qty_todo-pack_lot.qty)):
                        #     pack_lot.do_plus()
                    pack.write({'qty_done': pack.product_qty})
            transfer_dict = self.sudo().do_new_transfer()
            if type(transfer_dict) == dict and transfer_dict.get('res_model') and transfer_dict.get('res_id'):
                wiz_obj = self.env[transfer_dict['res_model']].sudo().browse(transfer_dict['res_id'])
                wiz_obj.process()
            backorder = self.search([('backorder_id', '=', self.id)], order='id desc', limit=1)
            if backorder:
                return backorder.id
            else:
                return self.id
        except:
            return 0

    @api.multi
    def do_new_transfer(self):
        ctx = {}
        for rec in self.filtered(lambda x: x.picking_type_code == 'outgoing'):
            line_list = []
            for line in rec.pack_operation_product_ids:
                vals = {}
                vals['product_id'] = line.product_id.id
                vals['qty'] = line.product_qty
                lot_list = []
                for pack_lot in line.pack_lot_ids:
                    lot_list.append({'lot_id': pack_lot.lot_id.id, 'qty': pack_lot.qty})
                vals['lot'] = lot_list
                line_list.append(vals)
            if 'picked_info' in ctx:
                ctx['picked_info'].update({rec.id: line_list})
            else:
                ctx.update({'picked_info': {rec.id: line_list}})
        return super(StockPicking, self.with_context(ctx)).do_new_transfer()

    # Partial Receiving Import
    @api.multi
    def _create_backorder(self, backorder_moves=[]):
        backorders = super(StockPicking, self)._create_backorder(backorder_moves)
        ctx = self._context or {}
        for backorder in backorders.filtered(lambda x: x.picking_type_code == 'outgoing'):
            backorder_of = backorder.backorder_id
            if ('picked_info' in ctx) and backorder_of and (backorder_of.id in ctx['picked_info']):
                picked_list = ctx['picked_info'][backorder_of.id]
                for i in picked_list:
                    for pack in backorder_of.pack_operation_product_ids.filtered(lambda x: x.product_id.id == i['product_id']):
                        if i['qty'] > pack.qty_done:
                            pass

        return backorders

StockPicking()

class StockMove(models.Model):
    _inherit = 'stock.move'

    sap_order_entry = fields.Integer()
    sap_line_number = fields.Integer()
    sap_order_line_number = fields.Integer()

StockMove()