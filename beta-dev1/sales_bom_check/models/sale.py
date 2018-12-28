# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning


class SaleOrderExtension(models.Model):
    _inherit = 'sale.order'

    def check_available_material(self, sale_line, bom_line):
        required_production =  sale_line.product_uom_qty - sale_line.product_id.qty_available
        if required_production < 0:
            return True
        else:
            material_for_one_product = bom_line.product_qty / bom_line.bom_id.product_qty
            if  bom_line.product_id.qty_available < (material_for_one_product * required_production):
                return False
            else:
                return True
    @api.model
    def compare_product_qty(self):
        filtered =  False
        filtered = self.order_line.filtered(lambda r: r.product_id.qty_available < r.product_uom_qty)
        if filtered and len(filtered) > 0 :
            return True
        return False

    @api.multi
    def action_confirm(self):
        if not self.compare_product_qty():
            return super(SaleOrderExtension, self).action_confirm()
        ir_model_data = self.env['ir.model.data']
        mrp_bom = self.env['mrp.bom']
        try:
            compose_form_id = ir_model_data.get_object_reference('sales_bom_check', 'view_sales_bom_check_wizard')[1]
        except ValueError:
            compose_form_id = False

        ctx = dict()
        order_line_list = []
        re_product_list = []
        for line in self.order_line:
            obj_list = []
            mrp_bom_obj = mrp_bom.search(
                [('product_id', '=', line.product_id.id), ('company_id', '=', self.company_id.id)])
            obj_list.append(mrp_bom_obj)

            if not mrp_bom_obj:
                mrp_bom_obj = mrp_bom.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                                              ('company_id', '=', self.company_id.id)])
                obj_list.append(mrp_bom_obj)

            if obj_list:
                count = 0
                for obj in obj_list:
                    for bom_line in obj.bom_line_ids:
                        # if bom_line.product_id.qty_available >= bom_line.product_qty:
                        #     state = 'available'
                        if self.check_available_material(line, bom_line):
                            state = 'available'
                        else:
                            state = 'not_available'
                        if count == 0:
                            item = {
                                'product_id': line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_qty_available': line.product_id.qty_available or 0.0,
                                'required_material_id': bom_line.product_id.id,
                                'req_product_qty': bom_line.product_qty * line.product_uom_qty,
                                'material_qty_available' :  bom_line.product_id.qty_available or 0.0,
                                # 'req_product_uom': line.product_uom.id,
                                'state': state,
                            }
                            order_line_list.append(item)
                            re_product_list.append(bom_line.product_id)
                        else:
                            item = {
                                'required_material_id': bom_line.product_id.id,
                                'req_product_qty': bom_line.product_qty * line.product_uom_qty,
                                'material_qty_available': bom_line.product_id.qty_available or 0.0,
                                'state': state,
                            }
                            order_line_list.append(item)
                            re_product_list.append(bom_line.product_id)
                        count += 1

        # print"\norder_line_list",order_line_list

        re_product_list = list(set(re_product_list))
        # print"\nre_product_list",re_product_list
        StockLoaction = self.env['stock.location']
        Quant = self.env['stock.quant']

        location_obj = StockLoaction.search(
            [('raw_material_check', '=', True), ('company_id', '=', self.company_id.id)])
        # print"location_obj",location_obj


        res = []
        for req_product in re_product_list:
            for location in location_obj:
                # print"location",location
                quant_objs = Quant.search([('product_id', '=', req_product.id),
                                           ('location_id', '=', location.id),
                                           ('location_id.company_id', '=', self.company_id.id),
                                           ])
                # print"quant_objs",quant_objs
                qty_list = [quant_obj.qty for quant_obj in quant_objs]
                total_qty = sum(qty_list)

                product_location = ''
                product_location = str(req_product.id) + '/' + str(location.id)

                res.append({
                    product_location: total_qty,
                })

        HTML = '<!DOCTYPE html><html><body><table border="1" cellspacing="50" width="100%"><tr><th>Product</th>'
        for location in location_obj:
            HTML += '<th>' + str(location.name) + '</th>'
        HTML += '</tr>'
        for product in re_product_list:
            HTML += '<tr><td>' + str(product.name) + '</td>'
            for location in location_obj:
                for item in res:
                    key = str(str(product.id) + '/' + str(location.id))
                    if key in item.keys():
                        HTML += '<td>' + str(item.get(key)) + '</td>'
            HTML += '</tr>'
        HTML += '</table></body></html>'
        ctx.update({
            'default_bom_check_line': order_line_list,
            'default_required_material_location_stock': HTML,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sales.bom.check',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class StockLocation(models.Model):
    _inherit = 'stock.location'

    raw_material_check = fields.Boolean('Raw Material Check')


class Sale_Oders_Line(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def compute_material_required(self):
        mrp_bom = self.env['mrp.bom']
        res = []
        if self.product_id.qty_available >= self.product_uom_qty:
            return None
        else:
            mrp_bom_obj = False
            required_product = self.product_uom_qty - self.product_id.qty_available
            mrp_bom_obj = mrp_bom.search(
                [('product_id', '=', self.product_id.id), ('company_id', '=', self.company_id.id)], limit=1)
            if not mrp_bom_obj:
                mrp_bom_obj = mrp_bom.search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
                                              ('company_id', '=', self.company_id.id)], limit=1)
            if mrp_bom_obj:
                for line in mrp_bom_obj.bom_line_ids:
                    material_need = 0.0
                    material_need = (line.product_qty / mrp_bom_obj.product_qty) * required_product
                    # compare material qty on hand and material qty need
                    if material_need > line.product_id.qty_available:
                        res.append((line.product_id, material_need, line.product_id.qty_available, line.product_uom_id))
        return res

    # @api.onchange('product_uom_qty')
    # def onchange_product_uom_qty(self):
    #     if self.product_id and self.product_uom_qty:
    #         computed = self.compute_material_required()
    #         if computed != []:
    #             warning_mess = {
    #                 'title': _('Not enough inventory!'),
    #                 'message': _(
    #                     'Not have enough Material:')
    #             }
    #             for val in computed:
    #                 warning_mess['message'] += '\n' + val[0].name + ' : ' + 'need %s %s but have only %s %s' % (
    #                     val[1], val[3].name or '', val[2], val[3].name or '')
    #             return {'warning': warning_mess}
    #     return
