from odoo import api, fields, models, _

class stock_inventory(models.Model):
    _inherit = 'stock.inventory'

    type = fields.Char('Form Type', compute='_compute_type')

    @api.multi
    def _compute_type(self):
        for record in self:
            if self.env.context.get('type', False):
                record.type = self.env.context.get('type')


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    view_type = fields.Char()

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        res = super(StockInventoryLine, self).read(fields=fields, load=load)
        type = self._context.get('type', False)
        if type == 'original' and 'product_uom_id' in fields and 'product_id' in fields:
            result = []
            for line in res:
                old_uom_id = line['product_uom_id']
                if isinstance(old_uom_id, tuple):
                    old_uom_id = old_uom_id[0]
                old_uom = self.env['product.uom'].browse(old_uom_id)

                product_id = line['product_id']
                if isinstance(product_id, tuple):
                    product_id = product_id[0]
                product = self.env['product.product'].browse(product_id)

                new_uom = product.product_tmpl_id.uom_po_id
                line['product_uom_id'] = new_uom.id
                if 'theoretical_qty' in line:
                    line['theoretical_qty'] = new_uom._compute_quantity(line['theoretical_qty'], old_uom)
                if 'purchased_qty' in line:
                    line['purchased_qty'] = new_uom._compute_quantity(line['purchased_qty'], old_uom)
                if 'original_received_qty' in line:
                    line['original_received_qty'] = new_uom._compute_quantity(line['original_received_qty'], old_uom)
                if 'adjusted_qty' in line:
                    line['adjusted_qty'] = new_uom._compute_quantity(line['adjusted_qty'], old_uom)
                result.append(line)
            return result
        return res