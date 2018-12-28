# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SalesBomCheck(models.TransientModel):
    _name = "sales.bom.check"
    _description = "Sales Bom Check"

    bom_check_line = fields.One2many('sales.bom.check.line', 'bom_check_id', string='Order Lines')
    required_material_location_stock = fields.Html("Required Material Location Stock")

    @api.multi
    def action_confirm(self):
        # print"\nWizard action_confirm()...",self

        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']
        for line in self.bom_check_line:
            # print"line",line
            if line.state == 'not_available':
                seller_ids = line.required_material_id.seller_ids
                # print"\n\nseller_ids",seller_ids
                if seller_ids:
                    # print"First seller_ids",seller_ids[0].id,seller_ids[0].name.id
                    po_obj = PurchaseOrder.search([('state', '=', 'draft'), ('partner_id', '=', seller_ids[0].name.id)],
                                                  order='id', limit=1)
                    # print"po_obj",po_obj

                    product_qty = line.req_product_qty - line.required_material_id.qty_available
                    # print"product_qty",product_qty

                    if po_obj:
                        pol_obj = PurchaseOrderLine.search(
                            [('order_id', '=', po_obj.id), ('product_id', '=', line.required_material_id.id)],
                            order='id', limit=1)
                        # print"pol_obj",pol_obj
                        if pol_obj:
                            product_qty = pol_obj.product_qty + product_qty
                            pol_obj.update({'product_qty': product_qty})
                        else:
                            line_vals = {
                                'order_id': po_obj.id,
                                'product_id': line.required_material_id.id,
                                'name': line.required_material_id.name,
                                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                'product_qty': product_qty,
                                'product_uom': line.required_material_id.uom_po_id.id,
                                'price_unit': line.required_material_id.uom_id.id,
                            }
                            # print"line_vals",line_vals
                            create_pol = PurchaseOrderLine.create(line_vals)
                        # print"create_pol",create_pol
                    else:
                        po_vals = {
                            'partner_id': seller_ids[0].name.id,
                        }
                        created_po = PurchaseOrder.create(po_vals)
                        # print"... created_po",created_po

                        line_vals = {
                            'order_id': created_po.id,
                            'product_id': line.required_material_id.id,
                            'name': line.required_material_id.name,
                            'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            'product_qty': product_qty,
                            'product_uom': line.required_material_id.uom_po_id.id,
                            'price_unit': line.required_material_id.uom_id.id,
                        }
                        # print"...line_vals",line_vals
                        create_pol = PurchaseOrderLine.create(line_vals)
                    # print"...create_pol",create_pol

        SaleOrder = self.env['sale.order']
        if self._context.get('active_id'):
            sale_order_obj = SaleOrder.browse(self._context.get('active_id'))
            for order in sale_order_obj:
                order.state = 'sale'
                order.confirmation_date = fields.Datetime.now()
                if sale_order_obj.env.context.get('send_email'):
                    sale_order_obj.force_quotation_send()
                order.order_line._action_procurement_create()
            if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
                sale_order_obj.action_done()
        return True


class SalesBomCheckLine(models.TransientModel):
    _name = "sales.bom.check.line"
    _description = "Sales Bom Check Lines"

    bom_check_id = fields.Many2one('sales.bom.check', string='Product')  # O2M
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)])
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                                   default=1.0)
    required_material_id = fields.Many2one('product.product', string='Required Material')
    req_product_qty = fields.Float(string='Required Quantity')
    # req_product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    state = fields.Selection([('available', 'Available'), ('not_available', 'Not Available')], string='Status',
                             readonly=True)
    product_qty_available = fields.Float(string='Quantity On Hand', digits=dp.get_precision('Product Unit of Measure'),
                                        default=0.0)
    material_qty_available = fields.Float(string='Quantity On Hand', digits=dp.get_precision('Product Unit of Measure'),
                                        default=0.0)

