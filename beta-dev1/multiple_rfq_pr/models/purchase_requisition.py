# -*- coding: utf-8 -*-

from odoo import fields, models, api

class purchase_requisition(models.Model):
    _inherit = 'purchase.requisition'

    vendor_ids      = fields.Many2many('res.partner',string='Vendor')

    @api.multi
    def action_create_po(self):
        for record in self:
            po_data = {}
            for vendor in record.vendor_ids:
                po_data = {
                    'partner_ref'    : record.name,
                    'origin'         : record.origin or record.name,
                    'date_order'     : record.ordering_date or fields.Date.today(),
                    'company_id'     : record.company_id.id,
                    'currency_id'    : record.company_id.currency_id.id,
                    'requisition_id' : record.id,
                    'picking_type_id': record.picking_type_id.id,
                    'partner_id'     : vendor.id,
                    'date_planned'   : record.schedule_date
                }
                po = record.env['purchase.order'].create(po_data)

                order_line = po.order_line.browse([])
                for requisition_line in record.line_ids:
                    line_data = {
                        'product_id'    : requisition_line.product_id.id,
                        'name'          : requisition_line.product_id.description or requisition_line.product_id.display_name,
                        'date_planned'  : requisition_line.schedule_date or fields.Date.today(),
                        'order_id'      : po.id,
                        'price_unit'    : requisition_line.price_unit,
                        'product_qty'   : requisition_line.product_qty,
                        'product_uom'   : requisition_line.product_uom_id,
                    }
                    order_line += po.order_line.new(line_data)
                po.order_line = order_line
        return






