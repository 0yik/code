# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from openerp.report import report_sxw
import base64
from reportlab.graphics.barcode import createBarcodeDrawing


class package_label_new(models.TransientModel):
    _name = 'package.label.new'
    
    pack_opreation_product_custom_ids = fields.Many2one('package.label', 'Pack Opreation')
    custom_product_id = fields.Many2one('product.product', 'Product')
    do_quantity = fields.Float('DO Quantity')
    lot_custom_number = fields.Many2one('stock.production.lot', 'Lot Number')
    lot_date = fields.Datetime('Lot Date')
    no_of_labels = fields.Integer('Number of Labels')
    label_quantity = fields.Float('Label Quantity', compute='calculate_label_quantity')
    line = fields.Many2one('stock.picking')
    
    @api.multi
    @api.onchange('no_of_labels')
    def calculate_label_quantity(self):
        for rec in self:
            if rec.do_quantity and rec.no_of_labels > 0:
                rec.label_quantity = (float(rec.do_quantity) / float(rec.no_of_labels))

    def barcode(self, type, value, width=600, height=100, humanreadable=0):
        width, height, humanreadable = int(width), int(height), bool(humanreadable)
        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable=humanreadable
        )
        return base64.encodestring(barcode_obj.asString('png'))


    
class package_label(models.TransientModel):
    _name = 'package.label'
    _description = 'Package Label'

    name = fields.Char('Name')
    do_line = fields.Many2one('stock.picking')
    pack_opration = fields.One2many('package.label.new', 'pack_opreation_product_custom_ids')

    @api.multi
    def yes(self):
        data = []
        lots = []
        lot_date = []
        dictionary = {}
        view = self.env.ref('package_label_printing.view_package_label_new')
        res_id = self.env['package.label'].create({})
        for rec in self.do_line.pack_operation_product_ids:
            lot = rec.pack_lot_ids
            if lot:
                for lot1 in lot:
                    if lot1:
                        lot2 = lot1.lot_id.id
                        lot3 = lot1.lot_id
            else:
                lot2 = False
            res2 = {'pack_opreation_product_custom_ids': res_id.id, 'lot_custom_number': lot2, 'lot_date': lot3.use_date, 'custom_product_id': rec.product_id.id, 'do_quantity': rec.qty_done, 'no_of_labels': self.pack_opration.no_of_labels, 'label_quantity': self.pack_opration.label_quantity}
            label = self.env['package.label.new'].create(res2)
            data.append(label)
            label['line'] = self.do_line
        return{
			'name': _('Package Label'),
	        'type': 'ir.actions.act_window',
	        'view_type': 'form',
	        'view_mode': 'form',
	        'res_model': 'package.label',
	        'views': [(view.id, 'form')],
	        'view_id': view.id,
	        'target': 'new',
	        'context': self.env.context,
	        'res_id': res_id.id,
            'nodestroy': False,
	    }
    def barcode(self, type, value, width=600, height=100, humanreadable=0):
        width, height, humanreadable = int(width), int(height), bool(humanreadable)
        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable=humanreadable
        )
        return base64.encodestring(barcode_obj.asString('png'))

    @api.multi
    def print_data(self):
        base64s = {}
        for rec in self.pack_opration:
            lot_nmber = rec.lot_custom_number.display_name
            base64s[lot_nmber] = self.barcode('Code128', lot_nmber)
        for rec in self.pack_opration:
            res = rec.line
            data = self.env["report"].get_action(self, 'package_label_printing.report_package')
            res.write({'state': 'done'})
            del data['report_type']
            data['report_file'] = True
            return data
            # return {
            #     'type': 'ir.actions.report.xml',
            #     'report_type': 'qweb-pdf',
            #     'report_name': 'package_label_printing.report_package',
            # }
    @api.multi
    def cancel(self):
        for rec in self:
            for opration in rec.pack_opration:
                data = opration.line
                data.write({'state': 'done'})
            return data

    @api.multi
    def no(self):
        for pick in self.do_line:
            if pick.state == 'done':
                raise UserError(_('The pick is already validated'))
            pack_operations_delete = self.env['stock.pack.operation']
            if not pick.move_lines and not pick.pack_operation_ids:
                raise UserError(_('Please create some Initial Demand or Mark as Todo and create some Operations. '))
            # In draft or with no pack operations edited yet, ask if we can just do everything
            if pick.state == 'draft' or all([x.qty_done == 0.0 for x in pick.pack_operation_ids]):
                # If no lots when needed, raise error
                picking_type = pick.picking_type_id
                if (picking_type.use_create_lots or picking_type.use_existing_lots):
                    for pack in pick.pack_operation_ids:
                        if pack.product_id and pack.product_id.tracking != 'none':
                            raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                view = self.env.ref('stock.view_immediate_transfer')
                wiz = self.env['stock.immediate.transfer'].create({'pick_id': pick.id})
                # TDE FIXME: a return in a loop, what a good idea. Really.
                return {
                    'name': _('Immediate Transfer?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.immediate.transfer',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }

            # Check backorder should check for other barcodes
            if pick.check_backorder():
                view = self.env.ref('stock.view_backorder_confirmation')
                wiz = self.env['stock.backorder.confirmation'].create({'pick_id': pick.id})
                # TDE FIXME: same reamrk as above actually
                return {
                    'name': _('Create Backorder?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.backorder.confirmation',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
            for operation in pick.pack_operation_ids:
                if operation.qty_done < 0:
                    raise UserError(_('No negative quantities allowed'))
                if operation.qty_done > 0:
                    operation.write({'product_qty': operation.qty_done})
                else:
                    pack_operations_delete |= operation
            if pack_operations_delete:
                pack_operations_delete.unlink()
        self.do_line.do_transfer()
        return