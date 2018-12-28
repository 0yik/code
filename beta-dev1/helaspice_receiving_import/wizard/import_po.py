from odoo import models, fields
import base64
from xlrd import open_workbook, xldate
from odoo.exceptions import UserError

class ImportPo(models.TransientModel):
    _name = 'import.po'
    _description = 'Import SAP PO'

    file = fields.Binary()
    filename = fields.Char()
    valid_data_ids = fields.One2many('import.po.line', 'import_id1', string='Valid Data')
    invalid_data_ids = fields.One2many('import.po.line', 'import_id2', string='Invalid Data')

    def action_validate(self):
        self.valid_data_ids.unlink()
        self.invalid_data_ids.unlink()
        data_file = base64.b64decode(self.file)
        try:
            wb = open_workbook(file_contents=data_file)
        except:
            raise UserError('Invalid file format')
        valid_data_list = []
        invalid_data_list = []
        for s in wb.sheets():
            for row in range(1, s.nrows):
                vals = {}
                data_row = []
                for col in range(s.ncols):
                    value = (s.cell(row, col).value)
                    data_row.append(value)
                if len(data_row) < 11:
                    raise UserError('Please check the columns in file are given as per the requirement.')
                sh_ref = str(data_row[1]).strip()
                if sh_ref:
                    sh_ref_id = self.env['shipment.reference'].search([('name', '=', sh_ref)], limit=1)
                    if not sh_ref_id:
                        sh_ref_id = self.env['shipment.reference'].create({'name': sh_ref})
                    vals['shipment_id'] = sh_ref_id
                    try:
                        vals['shipment_id'] = sh_ref_id
                    except:
                        vals['shipment_id'] = sh_ref_id
                else:
                    vals['shipment_id'] = False
                vals['sap_ref'] = str(data_row[2])
                try:
                    vals['sap_ref'] = str(float(vals['sap_ref']))[:-2]
                except:
                    pass
                vals['po_ref'] = str(data_row[3])
                vals['item_no'] = str(data_row[4])
                try:
                    vals['item_no'] = str(float(vals['item_no']))[:-2]
                except:
                    pass
                try:
                    vals['item_barcode'] = str(int(data_row[5]))
                except:
                    vals['item_barcode'] = str(data_row[5])
                product_id = False
                if vals['item_no']:
                    product_id = self.env['product.product'].search([('default_code', 'like', vals['item_no'])], limit=1)
                invalid_value = False
                try:
                    if data_row[7]:
                        float(data_row[7])
                    float(data_row[10])
                except:
                    invalid_value = True
                try:
                    vals['received_qty'] = str(int(data_row[7]))
                except:
                    vals['received_qty'] = str(data_row[7])
                vals['batch_no'] = str(data_row[8])
                try:
                    float(vals['batch_no'])
                    vals['batch_no'] = vals['batch_no'][:-2]
                except:
                    pass
                try:
                    bbd = xldate.xldate_as_datetime(int(data_row[9]), wb.datemode)
                    vals['bbd'] = str(bbd)[:10]
                    # datetime.strptime(str(data_row[9]), '%d-%m-%Y').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                except:
                    vals['bbd'] = False
                try:
                    vals['pl_qty'] = str(int(data_row[10]))
                except:
                    vals['pl_qty'] = str(data_row[10])
                vals['pallet_no'] = int(data_row[11])

                # Product
                if not product_id:
                    if data_row[6] and vals['item_no']:
                        product_vals = {}
                        product_vals['name'] = str(data_row[6])
                        product_vals['default_code'] = vals['item_no']
                        product_vals['type'] = 'product'
                        product_vals['barcode'] = vals['item_barcode']
                        if not vals['bbd'] or not vals['batch_no'] or not vals['item_barcode']:
                            product_vals['tracking'] = 'none'
                        else:
                            product_vals['tracking'] = 'lot'
                        product_id = self.env['product.product'].create(product_vals)
                    else:
                        product_id = False
                if not vals['bbd'] or not vals['batch_no'] or not vals['item_barcode']:
                    product_id.write({'barcode': vals['item_barcode'], 'default_code': vals['item_no'], 'tracking': 'none'})
                else:
                    product_id.write({'barcode': vals['item_barcode'], 'default_code': vals['item_no'], 'tracking': 'lot'})

                vals['product_id'] = product_id.id
                if (not vals['item_barcode']) and (vals['bbd'] or vals['batch_no']):
                    invalid_data_list.append((0, 0, vals))
                elif (not vals['shipment_id']) or (not vals['item_barcode']) or not (vals['po_ref']) or (not vals['product_id']) or (not vals['item_no']) or (not ['pl_qty']) or (invalid_value):
                    invalid_data_list.append((0, 0, vals))
                else:
                    valid_data_list.append((0, 0, vals))
        self.valid_data_ids = valid_data_list
        self.invalid_data_ids = invalid_data_list
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import(self):
        sh_ref_dict = {}
        lot_dict = {}
        for line in self.valid_data_ids:
            picking_type_id = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
            location_id = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_suppliers')
            location_dest_id = self.env['ir.model.data'].xmlid_to_res_id('stock.stock_location_stock')
            if '%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref) not in sh_ref_dict:
                vals = {}
                vals['origin'] = '%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref)
                vals['shipment_id'] = line.shipment_id.id
                vals['picking_type_id'] = picking_type_id.id
                vals['location_id'] = location_id
                vals['location_dest_id'] = location_dest_id
                vals['pallet_no'] = line.pallet_no
                vals['po_reference'] = line.po_ref
                picking_id = self.env['stock.picking'].create(vals)
                sh_ref_dict.update({'%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref): picking_id.id})
            move_vals = {}
            move_vals['picking_id'] = sh_ref_dict.get('%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref), False)
            move_vals['product_id'] = line.product_id.id
            move_vals['name'] = line.product_id.name
            move_vals['product_uom_qty'] = float(line.pl_qty)
            move_vals['product_uom'] = line.product_id.uom_id.id if line.product_id and line.product_id.uom_id else False
            move_vals['location_id'] = location_id
            move_vals['location_dest_id'] = location_dest_id
            move_vals['po_ref'] = line.po_ref
            try:
                float(line.sap_ref)
                move_vals['sap_ref'] = str(float(line.sap_ref))[:-2]
            except:
                move_vals['sap_ref'] = str(line.sap_ref)
            move_obj = self.env['stock.move'].create(move_vals)
            move_id = move_obj.id
            if (sh_ref_dict.get('%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref), False)) and (sh_ref_dict.get('%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref), False) not in lot_dict):
                lot_dict.update({sh_ref_dict['%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref)]: {}})
            if (sh_ref_dict.get('%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref), False)):
                if line.product_id.id in lot_dict[sh_ref_dict['%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref)]]:
                    lot_dict[sh_ref_dict['%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref)]][line.product_id.id].update({move_id: [str(line.batch_no), float(line.pl_qty), str(line.bbd)[:10]]})
                else:
                    lot_dict[sh_ref_dict['%s - %s - %s'% (line.pallet_no, line.shipment_id.name, line.po_ref)]].update({line.product_id.id: {move_id: [str(line.batch_no), float(line.pl_qty), str(line.bbd)[:10]]}})
        for pick_id in sh_ref_dict.values():
            picking_obj = self.env['stock.picking'].browse(pick_id)
            picking_obj.action_confirm()
            for pack_id in picking_obj.pack_operation_product_ids:
                if pack_id.product_id.id in lot_dict[sh_ref_dict[picking_obj.origin]]:
                    for i in lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id].keys():
                        vals = {}
                        lot_name = lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][0]
                        if lot_name:
                            full_batch = '010'
                        elif str(lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][2]) and str(lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][2]) != 'False':
                            full_batch = '020'
                        else:
                            full_batch = ''
                        if pack_id.product_id.barcode:
                            try:
                                full_batch += str(int(pack_id.product_id.barcode))
                            except:
                                full_batch += str(pack_id.product_id.barcode)
                        use_date = str(lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][2])
                        if use_date and str(use_date) != 'False':
                            full_batch += '15'
                            try:
                                full_batch += use_date[2:4] + use_date[5:7] + use_date[8:10]
                            except:
                                pass
                        try:
                            float(lot_name)
                            lot_name = str(float(lot_name))[:-2]
                        except:
                            pass
                        if lot_name:
                            full_batch += '10'
                            if len(lot_name) > 8:
                                full_batch += lot_name[:8]
                            else:
                                full_batch += lot_name
                        lot_id = self.env['stock.production.lot'].search([('name', '=', full_batch), ('product_id', '=', pack_id.product_id.id)], limit=1)
                        if not lot_id:
                            lot_vals = {}
                            lot_vals['name'] = str(full_batch)
                            lot_vals['batch_no'] = lot_name
                            lot_vals['product_id'] = pack_id.product_id.id
                            if lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][2] and str(lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][2]) != 'False':
                                lot_vals['use_date'] = str(lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][2])+' 00:00:00'
                            lot_id = self.env['stock.production.lot'].create(lot_vals)
                        exist_batch = self.env['manage.incoming.batch'].search([('origin', '=', picking_obj.origin), ('lot_id', '=', lot_id.id)], limit=1)
                        if exist_batch:
                            exist_batch.write({'qty': exist_batch.qty + lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][1],
                                               'picking_ids': [(4, pick_id)]})
                        else:
                            vals['origin'] = picking_obj.origin
                            vals['shipment_id'] = picking_obj.shipment_id.id
                            vals['picking_ids'] = [(4, pick_id)]
                            vals['lot_id'] = lot_id.id
                            vals['qty'] = lot_dict[sh_ref_dict[picking_obj.origin]][pack_id.product_id.id][i][1]
                            vals['product_id'] = pack_id.product_id.id
                            vals['pallet_no'] = picking_obj.pallet_no
                            vals['po_reference'] = picking_obj.po_reference
                            self.env['manage.incoming.batch'].create(vals)
        return True

ImportPo()

class ImportPoLine(models.TransientModel):
    _name = 'import.po.line'
    _description = 'Import SAP PO Data'

    import_id1 = fields.Many2one('import.po')
    import_id2 = fields.Many2one('import.po')
    shipment_id = fields.Many2one('shipment.reference', readonly=True, string='Shipment')
    sap_ref = fields.Char('SAP Reference')
    po_ref = fields.Char('PO Reference')
    item_no = fields.Char('Item No')
    item_barcode = fields.Char('Item Barcode')
    product_id = fields.Many2one('product.product', string='Item Description')
    received_qty = fields.Char('Received Qty')
    batch_no = fields.Char('Batch Number (P/L)')
    bbd = fields.Date('BBD')
    pl_qty = fields.Char('PL Qty')
    pallet_no = fields.Integer('Pallet No')

ImportPoLine()