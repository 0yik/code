# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import Warning


class ReorderPO(models.TransientModel):
    _name = 'reorder.po'

    #TODO Change function create PO to PR
    @api.multi
    def reorder_po_calculation(self):
        def_supplier = self.env.ref('reorder_sales.partner_default_supplier')
        check = self.env.user.has_group('base.group_system')
        # product_obj = self.env['purchase.order']
        purchase_req_obj = self.env['purchase.request']
        bom_obj = self.env['mrp.bom']

        ir_values_obj = check and self.env['ir.values'].sudo() or self.env['ir.values']
        number_of_days = ir_values_obj.get_default('purchase.config.settings', 'number_of_days')
        reorder_buffer = ir_values_obj.get_default('purchase.config.settings', 'reorder_buffer')

        if not number_of_days:
             raise Warning(_('Please set number of days for startign calculation.'))
        calculate_date = datetime.now() - timedelta(days=number_of_days)
        # Change to is_created_pr
        order_ids = self.env['pos.order'].search([('is_created_pr', '=', False), ('date_order', '<=', datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)) , ('date_order', '>=', calculate_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))])
        if order_ids:
            product_details = {}
            # for line_id in [line_id for order in order_ids for line_id in order.lines]:
            #     product_details.update({line_id.product_id.id: product_details.get(line_id.product_id.id, 0) + line_id.qty})
            # uom_id = self.env['product.uom'].search([('name', '=', 'Unit(s)')])[0]
            for order in order_ids:
                for line in order.lines:
                    if line.product_id and line.product_id.product_ctg == 'ppic':
                        product_details.update({line.product_id.id: product_details.get(line.product_id.id, 0) + line.qty})
                    else:
                        boms = bom_obj.search([('product_tmpl_id','=',line.product_id.product_tmpl_id.id)])
                        for bom in boms:
                            for bom_line in bom.bom_line_ids:
                                qty_line = (line.qty * bom_line.product_qty) / bom.product_qty
                                product_details.update({bom_line.product_id.id: product_details.get(bom_line.product_id.id, 0) + qty_line})

            product_vals = []
            for product in product_details.items():
                product_id = self.env['product.product'].search([('id', '=', product[0])])
                quantity = product[1]*(100 + reorder_buffer)/100
                product_vals.append((0, 0, {'product_id': product[0],
                    'product_qty': quantity,
                    'name': product_id.name,
                    'date_required': datetime.today(),
                    'state': 'to_approve',
                    # 'product_qty': product[1],
                    # 'product_uom': uom_id.id,
                    # 'price_unit': product_id.standard_price,
                    # 'taxes_id': [(6,0, product_id.supplier_taxes_id.ids)],
                    # 'date_planned': datetime.today(),
                    }))

            # part_id = self.env.ref('centralkitchen_po.partner_central_kitchen')
            pr_vals = {
                # 'partner_id':part_id.id,
                # 'order_line': product_vals,
                'requested_by':self.env.user.id,
                'line_ids': product_vals,
            }
            # par_id = product_obj.create(order_vals)
            purchase_req_id = purchase_req_obj.create(pr_vals)
            #purchase_req_id.button_to_approve()
            or_ids = order_ids.write({'is_created_pr': True})
            
