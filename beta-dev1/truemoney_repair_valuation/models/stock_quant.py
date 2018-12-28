from odoo import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    repair_id = fields.Many2one('mrp.repair', string="Repair Ref")

StockMove()

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _compute_inventory_value(self):
        for quant in self:
            add_product = 0.0
            remove_product = 0.0
            repair = False
            if quant.company_id != self.env.user.company_id:
                # if the company of the quant is different than the current user company, force the company in the context
                # then re-do a browse to read the property fields for the good company.
                quant = quant.with_context(force_company=quant.company_id.id)
            quant.inventory_value = quant.product_id.standard_price * quant.qty
            for move_id in quant.history_ids:
                if move_id.repair_id:
                    repair = True
                    repair_objs = self.env['mrp.repair'].search([('move_id','=',move_id.id)])
                    for repair_obj in repair_objs:
                        main_product_price = repair_obj.product_id.standard_price
                        for repair_line in repair_obj.operations:
                            if repair_line.type == 'add':
                                add_product += repair_line.price_unit
                            if repair_line.type == 'remove':
                                remove_product += repair_line.price_unit
            if repair:
                quant.inventory_value = main_product_price + add_product - remove_product

StockMove()