from odoo import models, fields, api

class Inventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def default_get(self, fields_list):
        res = super(Inventory, self).default_get(fields_list)
        res['responsible_id'] = self.env.user.id if self.env.user else False
        return res

    responsible_id = fields.Many2one('res.users', string='Responsible')

    def get_inventory_list(self, user_id):
        data_dict = {}
        for inv_id in self.search([('responsible_id', '=', user_id), ('state', '=', 'confirm')]).filtered(lambda x: x.line_ids and any(line.product_qty - line.theoretical_qty for line in x.line_ids)):
            vals = {}
            vals['stock_take_id'] = inv_id.id
            vals['ref'] = inv_id.name
            date = str(inv_id.date)[:10] if inv_id.date else ''
            vals['date'] = date
            try:
                location = inv_id.location_id.name_get()
                vals['location'] = location[0][1]
            except:
                pass
            if date in data_dict:
                data_dict[date].append(vals)
            else:
                data_dict[date] = [vals]
        return data_dict

    def get_inventory_data(self):
        self.ensure_one()
        data_list = []
        for line in self.line_ids:
            if line.product_qty - line.theoretical_qty:
                vals = {}
                vals['line_id'] = line.id
                if line.product_id:
                    vals['product'] = line.product_id.name
                    vals['barcode'] = line.product_id.barcode
                    vals['item_no'] = line.product_id.default_code
                vals['qty'] = line.product_qty - line.theoretical_qty
                try:
                    location = line.location_id.name_get()
                    vals['location'] = location[0][1]
                except:
                    pass
                data_list.append(vals)
        return data_list

Inventory()
