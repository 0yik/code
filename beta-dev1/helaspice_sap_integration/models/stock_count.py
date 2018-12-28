from odoo import models, fields
import requests
import json
from requests.auth import HTTPBasicAuth
from odoo.exceptions import UserError

class StockCount(models.Model):
    _inherit = 'stock.count'

    sap_count_id = fields.Integer(copy=False, string='SAP Count ID')

    def create_stock_count(self, count_dict):
        try:
            if not count_dict.get('Lines', []):
                return 0
            vals = {}
            vals['name'] = count_dict.get('Ref2', False)
            vals['sap_count_id'] = int(count_dict.get('CountID', 0))
            vals['remarks'] = count_dict.get('Remarks', False)
            vals['state'] = 'open'
            if count_dict.get('CountDate', False):
                vals['count_date'] = str(count_dict['CountDate'])[:10]
            line_list = []
            for line_dict in count_dict.get('Lines', []):
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
                if product_id and float(line_dict.get('CountQty', 0)):
                    line_vals = {}
                    line_vals['product_id'] = product_id.id
                    line_vals['qty'] = float(line_dict.get('CountQty', 0))
                    line_vals['sap_line_number'] = int(line_dict.get('LineNumber', 0))
                    line_list.append((0, 0, line_vals))
            vals['line_ids'] = line_list
            count_id = self.env['stock.count'].create(vals)
            return count_id.id
        except:
            return 0

    def push_stock_count(self):
        url = self.env['ir.config_parameter'].get_param('sap.url', default=None)
        username = self.env['ir.config_parameter'].get_param('sap.username', default=None)
        password = self.env['ir.config_parameter'].get_param('sap.password', default=None)
        if not url or not username or not password:
            raise UserError('Invalid configuration for SAP.')
        url += '/POST_STOCKCOUNT'
        headers = {'content-type': 'application/json'}
        vals = {}
        vals['CountID'] = self.sap_count_id
        vals['Ref2'] = self.name
        vals['remarks'] = self.remarks
        line_list = []
        for line in self.line_ids:
            line_vals = {}
            line_vals['CountID'] = self.sap_count_id
            line_vals['LineNumber'] = line.sap_line_number
            line_vals['ItemCode'] = line.product_id.default_code
            line_vals['CountQty'] = line.qty
            line_vals['Counted'] = line.count_qty
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
            if line.count_lot_ids:
                lot_dict = {}
                if line_vals['IsSerial'] == 'Y':
                    for line_lot in line.count_lot_ids.filtered(lambda x: x.lot_id):
                        if line_lot.lot_id.name in lot_dict:
                            lot_dict[line_lot.lot_id.name]['Quantity'] += line_lot.qty
                        else:
                            lot_vals = {}
                            lot_vals['CountID'] = self.sap_count_id
                            lot_vals['LineNumber'] = line.sap_line_number
                            lot_vals['SerialNumber'] = line_lot.display_batch_no if line_lot.display_batch_no else ''
                            lot_vals['Quantity'] = line_lot.qty
                            lot_vals['ExpiryDate'] = line_lot.display_bbd[:10] if line_lot.display_bbd else ''
                            lot_dict[line_lot.lot_id.name] = lot_vals
                    for l in lot_dict.keys():
                        serial_list.append(lot_dict[l])
                elif line_vals['IsBatch'] == 'Y':
                    for line_lot in line.count_lot_ids.filtered(lambda x: x.lot_id):
                        if line_lot.lot_id.name in lot_dict:
                            lot_dict[line_lot.lot_id.name]['Quantity'] += line_lot.qty
                        else:
                            lot_vals = {}
                            lot_vals['CountID'] = self.sap_count_id
                            lot_vals['LineNumber'] = line.sap_line_number
                            lot_vals['BatchNumber'] = line_lot.display_batch_no if line_lot.display_batch_no else ''
                            lot_vals['ExpiryDate'] = line_lot.display_bbd[:10] if line_lot.display_bbd else ''
                            lot_vals['Quantity'] = line_lot.qty
                            lot_dict[line_lot.lot_id.name] = lot_vals
                    for l in lot_dict.keys():
                        batch_list.append(lot_dict[l])
            line_vals['Serial'] = serial_list
            line_vals['Batch'] = batch_list
            line_list.append(line_vals)
        vals['Lines'] = line_list
        try:
            request = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(vals))
            response = request.json()
            self.message_post(response)
        except:
            raise UserError('Invalid Configuration')

StockCount()

class StockCountLine(models.Model):
    _inherit = 'stock.count.line'

    sap_line_number = fields.Integer('Line Number')

StockCountLine()