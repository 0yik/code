# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class ResAssemble(models.Model):
    _name = 'res.assemble'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'Product Assemble'

    material_id = fields.One2many('assemble.materials','assemble_id','Materials', readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', True)]}, index=True, default='New')
    product_id = fields.Many2one('product.template', 'Product',readonly=True, states={'draft': [('readonly', False)]})
    product_product_id = fields.Many2one('product.product', compute='_compute_product_id', string='Product (2)')
    quantity_pro = fields.Integer('Quantity',readonly=True, states={'draft': [('readonly', False)]},default=1)
    date_assemble = fields.Date('Date',readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    stock_production_prod = fields.Many2one('stock.production.lot','Serial Number',readonly=True, states={'draft': [('readonly', False)]})
    location_src_id = fields.Many2one('stock.location','Location',readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),('cancel','Cancelled')], string='Status', default='draft')

    @api.depends('product_id')
    def _compute_product_id(self):
        for record in self:
            product = self.env['product.product'].search([('product_tmpl_id','=',record.product_id.id)], limit=1)
            record.product_product_id = product.id

    @api.onchange('product_id', 'quantity_pro')
    def onchange_product_id(self):
        if self.product_id:
            data = []
            for line in self.product_id.material_ids:
                data.append((0, 0, {'product_id': line.product_id.id, 'qty_pro': line.material_quantity * self.quantity_pro}))
            self.material_id = data

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('res.assemble') or 'New'
        result = super(ResAssemble, self).create(vals)
        if result.material_id and result.stock_production_prod:
            result.stock_production_prod.write({'material_ids': [(6, 0 , [result.material_id.ids])]})
        return result

    @api.multi
    def write(self, vals):
        result = super(ResAssemble, self).write(vals)
        if self.material_id and self.stock_production_prod:
            self.stock_production_prod.write({'material_ids': [(6, 0 , [self.material_id.ids])]})
        return result

    @api.multi
    def compute_product_qty(self, product_id):
        quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',product_id),('location_id','=',self.location_src_id.id)])
        return sum([quant.qty for quant in quant_ids])

    @api.multi
    def action_assemble(self):
        if not self.material_id:
            raise UserError('Can not assemble without materials')
        for line in self.material_id:
            available_qty = self.compute_product_qty(line.product_id.id)
            if line.qty_pro > available_qty:
                raise UserError('%s : Quantity greater than the on hand quantity (%s)' % (line.product_id.name, available_qty))
        dest_location = self.env['stock.location'].search([('usage', '=', 'production')], limit=1)
        # Calculating the product_data from the materials
        product_data = {}
        for line in self.material_id:
            if line.product_id.id not in product_data:
                product_data.update({line.product_id.id: line.qty_pro})
            else:
                product_data.update({line.product_id.id: line.qty_pro + product_data.get(line.product_id.id)})

        for record in self:
            product_obj = self.env['product.product'].search([('product_tmpl_id','=',record.product_id.id)], limit=1)
            # increasing qty of main product
            vals = {
                'product_id': product_obj.id,
                'product_uom_qty': record.quantity_pro,
                'product_uom': product_obj.uom_id.id,
                'name': product_obj.name,
                'date_expected': fields.Datetime.now(),
                'procure_method': 'make_to_stock',
                'location_id': dest_location.id,
                'location_dest_id': record.location_src_id.id,
                'origin': record.name,
                'restrict_lot_id': record.stock_production_prod.id or False,
            }
            move = self.env['stock.move'].create(vals)
            move.action_confirm()
            move.action_done()

            # decreasing material qty
            for product_id in product_data:
                if product_data.get(product_id):
                    lot_line_id = self.env['assemble.materials'].search([('assemble_id','=',record.id),('product_id','=',product_id)])
                    product_obj = self.env['product.product'].browse(product_id)
                    stock_move = {
                        'product_id': product_obj.id,
                        'product_uom_qty': product_data.get(product_id),
                        'product_uom': product_obj.uom_id.id,
                        'name': product_obj.name,
                        'date_expected': fields.Datetime.now(),
                        'procure_method': 'make_to_stock',
                        'location_id': record.location_src_id.id,
                        'location_dest_id': dest_location.id,
                        'origin': record.name,
                        'restrict_lot_id': lot_line_id.stock_lot.id or False,
                    }
                    move = self.env['stock.move'].create(stock_move)
                    move.action_confirm()
                    move.action_done()

        self.write({'state': 'done'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

ResAssemble()

class AssembleMaterials(models.Model):
    _name = 'assemble.materials'

    assemble_id = fields.Many2one('res.assemble', 'Materials')
    product_id = fields.Many2one('product.product', 'Product')
    qty_pro = fields.Integer('Quantity')
    stock_lot = fields.Many2one('stock.production.lot', 'Serial Number')

AssembleMaterials()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def assemble_form_view(self):
        ctx = dict()
        form_id = self.env['ir.model.data'].sudo().get_object_reference('simple_assemble_disassemble', 'res_assemble_form_view')[1]
        ctx.update({
            'default_product_id': self.id,
        })
        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.assemble',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,
        }
        return action

ProductTemplate()
