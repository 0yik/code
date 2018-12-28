from odoo import models, fields, api, _
from odoo.exceptions import UserError

import json


class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    recommend_sn = fields.Char('Recommended Serial Numbers', compute='_compute_barcode_showsn')
    scaned_sn    = fields.Char('Scanned Serial Numbers', compute='_compute_barcode_showsn')

    @api.multi
    @api.depends('product_id', 'pack_lot_ids', 'picking_id')
    def _compute_barcode_showsn(self):
        Lot = self.env['stock.production.lot']
        for record in self:
            if record.product_id:
                if record.product_id.tracking != 'none' and record.picking_id and record.picking_id.picking_type_id.code == 'outgoing' and record.picking_id.picking_type_id.name == 'Delivery Orders':
                    # if record.product_id.barcode:
                    #     record.recommend_sn = record.product_id.barcode or ''
                    # else:
                    scaned_sns = []
                    recommend_sns = []
                    for pack in record.pack_lot_ids:
                        if pack.lot_id and pack.lot_id.name:
                            if pack.qty >= 1:
                                scaned_sns.append(pack.lot_id.name)
                            recommend_sns.append(pack.lot_id.name)
                    record.recommend_sn = '||'.join(recommend_sns)
                    record.scaned_sn = '||'.join(scaned_sns)
                else:
                    record.recommend_sn = ''
                    record.scaned_sn = ''
                    continue

#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type,
#                                                         toolbar=toolbar, submenu=False)
#         if self._context.get('params', False) and view_type == 'form':
#             if self._context.get('params').get('id', False) and self._context.get('params').get('view_type',
#                                                                                                 '') == 'form':
#                 picking = self.search([('id', '=', self._context['params']['id'])])
#                 if picking and not (
#                                 picking.picking_type_id.code == 'outgoing' and picking.picking_type_id.name == 'Delivery Orders'):
#                     arch = False
#                     try:
#                         arch = res['fields']['pack_operation_product_ids']['views']['tree']['arch']
#                     except:
#                         return res
#                     if arch:
#                         try:
#                             arch = arch.replace('name="recommend_sn" modifiers="{&quot;readonly&quot;: true}"',
#                                                 'name="recommend_sn" invisible="1" modifiers="{&quot;readonly&quot;: true, &quot;tree_invisible&quot;: true}"')
#                             arch = arch.replace('name="scaned_sn" modifiers="{&quot;readonly&quot;: true}"',
#                                                 'name="scaned_sn" invisible="1" modifiers="{&quot;readonly&quot;: true, &quot;tree_invisible&quot;: true}"')
#                             res['fields']['pack_operation_product_ids']['views']['tree']['arch'] = arch
#                         except:
#                             return res
#         return res
class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.lot_id and record.lot_id.name:
                result.append((record.id, record.lot_id.name))
            elif record.lot_name:
                result.append((record.id, record.lot_name))
            else:
                result.append((record.id, str(record.id)))
        return result