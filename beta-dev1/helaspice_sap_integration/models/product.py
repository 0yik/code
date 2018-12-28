from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def create_products(self, data_dict):
        try:
            if data_dict.get('ItemCode', False):
                product_id = self.env['product.product'].search([('default_code', '=', data_dict['ItemCode'])], limit=1)
                if not product_id:
                    product_id = self.env['product.product'].search([('default_code', '=', data_dict['ItemCode']), ('active', '=', False)], limit=1)
                vals = {}
                vals['name'] = data_dict.get('Description', '')
                vals['default_code'] = data_dict.get('ItemCode', '')
                vals['barcode'] = data_dict.get('ItemBarcode', '')
                vals['type'] = 'product'
                vals['rack_location'] = data_dict.get('RackLocation', '')
                if data_dict.get('IsSerial', 'N') == 'Y':
                    vals['tracking'] = 'serial'
                elif data_dict.get('IsBatch', 'N') == 'Y':
                    vals['tracking'] = 'lot'
                else:
                    vals['tracking'] = 'none'
                if data_dict.get('Active', False):
                    if data_dict.get('Active') == 'N':
                        vals['active'] = False
                    else:
                        vals['active'] = True
                if product_id:
                    vals['active'] = True
                    product_id.write(vals)
                    return product_id.id
                else:
                    product_id = self.env['product.product'].create(vals)
                    return product_id.id
            else:
                return 0
        except:
            return 0

    def edit_products(self, data_dict):
        try:
            if data_dict.get('ItemCode', False):
                product_id = self.env['product.product'].search([('default_code', '=', data_dict['ItemCode'])], limit=1)
                if not product_id:
                    product_id = self.env['product.product'].search([('default_code', '=', data_dict['ItemCode']), ('active', '=', False)], limit=1)
                vals = {}
                vals['name'] = data_dict.get('Description', '')
                vals['barcode'] = data_dict.get('ItemBarcode', '')
                vals['rack_location'] = data_dict.get('RackLocation', '')
                if data_dict.get('NoTracking', 'N') == 'Y':
                    vals['tracking'] = 'none'
                elif data_dict.get('IsSerial', 'N') == 'Y':
                    vals['tracking'] = 'serial'
                elif data_dict.get('IsBatch', 'N') == 'Y':
                    vals['tracking'] = 'lot'
                if data_dict.get('Active', False):
                    if data_dict.get('Active') == 'N':
                        vals['active'] = False
                    else:
                        vals['active'] = True
                if not product_id:
                    self.env['product.product'].create(vals)
                    return 'Successful Call'
                product_id.write(vals)
                return 'Successful Call'
            return 'Unsuccessful Call'
        except:
            return 'Unsuccessful Call'

ProductProduct()
