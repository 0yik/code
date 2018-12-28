from odoo import api, fields, models, _

class StockQuant(models.Model):

    _inherit = 'stock.quant'

    type = fields.Char('Form Type', compute='_compute_type')
    purchase_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure', compute='_compute_product_uom_id', related=False, readonly=True)


    @api.multi
    def _compute_type(self):
        for record in self:
            if self.env.context.get('type', False):
                record.type = self.env.context.get('type')

    @api.multi
    def _compute_product_uom_id(self):
        for record in self:
            if record.purchase_uom_id:
                record.product_uom_id = record.purchase_uom_id
            elif record.product_id:
                record.product_uom_id = record.product_id.uom_id

    def _quant_create_from_move(self, qty, move, lot_id=False, owner_id=False, src_package_id=False,
                                dest_package_id=False, force_location_from=False, force_location_to=False):
        quant = super(StockQuant, self)._quant_create_from_move(qty, move, lot_id=lot_id, owner_id=owner_id,
                                                                src_package_id=src_package_id,
                                                                dest_package_id=dest_package_id,
                                                                force_location_from=force_location_from,
                                                                force_location_to=force_location_to)
        quant.sudo().write({
            'qty': move.product_uom_qty,
            'purchase_uom_id': move.product_uom.id,
        })
        return quant

        # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     res = super(StockQuant, self).search_read(domain=domain, fields=fields, offset=offset,
    #                                                limit=limit, order=order)
    #     type = self._context.get('type', False)
    #     if type == 'original':
    #         result = []
    #         for quant in res:
    #             old_uom_id = quant['product_uom_id'][0]
    #             old_uom = self.env['product.uom'].browse(old_uom_id)
    #             product = self.env['product.product'].browse(quant['product_id'][0])
    #             quant['product_uom_id'] = (product.product_tmpl_id.uom_po_id.id, product.product_tmpl_id.uom_po_id.name)
    #             quant['qty'] = product.product_tmpl_id.uom_po_id._compute_quantity(quant['qty'], old_uom)
    #             result.append(quant)
    #         return result
    #     return res
    #
    # @api.multi
    # def read(self, fields=None, load='_classic_read'):
    #     res = super(StockQuant, self).read(fields=fields, load=load)
    #     type = self._context.get('type', False)
    #     if type == 'original' and 'product_uom_id' in fields and 'product_id' in fields:
    #         result = []
    #         for line in res:
    #             old_uom_id = line['product_uom_id']
    #             if isinstance(line['product_uom_id'], tuple):
    #                 old_uom_id = old_uom_id[0]
    #             old_uom = self.env['product.uom'].browse(old_uom_id)
    #
    #             product_id = line['product_id']
    #             if isinstance(line['product_id'], tuple):
    #                 product_id = product_id[0]
    #             product = self.env['product.product'].browse(product_id)
    #
    #             new_uom = product.product_tmpl_id.uom_po_id
    #             if isinstance(line['product_uom_id'], tuple):
    #                 line['product_uom_id'] = (new_uom.id, new_uom.name)
    #             else:
    #                 line['product_uom_id'] = new_uom.id
    #
    #             if 'qty' in line:
    #                 line['qty'] = new_uom._compute_quantity(line['qty'], old_uom)
    #             result.append(line)
    #         return result
    #     return res

class StockMove(models.Model):
    _inherit = "stock.move"

    view_type = fields.Char()

    # @api.multi
    # def read(self, fields=None, load='_classic_read'):
    #     result = []
    #     type = self._context.get('type', False)
    #     if type == 'original' and 'product_uom_qty' in fields:
    #         fields.append('product_uom')
    #         fields.append('product_id')
    #         res = super(StockMove, self).read(fields=fields, load=load)
    #         for line in res:
    #             product_id = line['product_id']
    #             if isinstance(product_id, tuple):
    #                 product_id = product_id[0]
    #             product = self.env['product.product'].browse(product_id)
    #
    #             old_uom = product.uom_id
    #
    #             new_uom = product.product_tmpl_id.uom_po_id
    #             line['product_uom_qty'] = new_uom._compute_quantity(line['product_uom_qty'], old_uom)
    #
    #             result.append(line)
    #         return result
    #     else:
    #         result = super(StockMove, self).read(fields=fields, load=load)
    #     return result