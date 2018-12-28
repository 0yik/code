from odoo import models, api

class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    # For the app
    def get_picking_list(self, user_id, picking_type):
        data_list = []
        data_dict = {}
        status_dict = {'confirmed': 'Waiting', 'partially_available': 'Partially Picked', 'assigned': 'Ready'}
        for pick_wave in self.search([('user_id', '=', user_id), ('state', '=', 'in_progress')]):
            if picking_type in ['incoming', 'outgoing']:
                picking_ids = pick_wave.picking_ids.filtered(lambda x: x.state in ['partially_available', 'assigned'] and x.picking_type_code == picking_type)
            else:
                picking_ids = pick_wave.picking_ids.filtered(lambda x: x.state in ['confirmed', 'partially_available', 'assigned'] and x.picking_type_code == 'outgoing')
            for picking_id in picking_ids:
                vals = {}
                vals['picking_id'] = picking_id.id
                vals['name'] = picking_id.name
                vals['backorder'] = picking_id.backorder_id.name if picking_id.backorder_id else ''
                vals['ref'] = picking_id.origin
                vals['shipment_ref'] = picking_id.shipment_id.name if picking_id.shipment_id else False
                vals['date_scheduled'] = str(picking_id.min_date)[:10] if picking_id.min_date else ''
                vals['partner'] = picking_id.partner_id.name if picking_id.partner_id else ''
                if (picking_type == 'picking') and (picking_id.state == 'assigned'):
                    vals['status'] = 'Picked'
                else:
                    vals['status'] = status_dict.get(picking_id.state, '')
                vals['remarks'] = picking_id.note.strip() if picking_id.note else ''
                if picking_type == 'incoming':
                    vals['pallet_no'] = str(picking_id.pallet_no) if picking_id.pallet_no else 'No Pallet'
                    vals['po_reference'] = picking_id.po_reference
                    shipment_ref = picking_id.shipment_id.name if picking_id.shipment_id else 'No Shipment'
                    if shipment_ref in data_dict:
                        if vals['pallet_no'] in data_dict[shipment_ref]:
                            data_dict[shipment_ref][vals['pallet_no']].append(vals)
                        else:
                            data_dict[shipment_ref][vals['pallet_no']] = [vals]
                    else:
                        data_dict[shipment_ref] = {}
                        data_dict[shipment_ref][vals['pallet_no']] = [vals]
                else:
                    data_list.append(vals)
        if picking_type == 'incoming':
            return data_dict
        else:
            return data_list

    @api.multi
    def confirm_picking(self):
        # pickings_todo = self.mapped('picking_ids')
        self.write({'state': 'in_progress'})
        # pickings_todo.filtered(lambda picking: picking.state == 'draft' and picking.picking_type_code == 'outgoing').action_confirm()
        # pickings_todo.filtered(lambda picking: picking.picking_type_code == 'incoming').action_assign()
        return True

StockPickingWave()