# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class ResDisassemble(models.Model):
    _name = 'res.disassemble'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'Product Disassemble'

    material_id = fields.One2many('disassemble.materials','disassemble_id','Disassemble',readonly=True, states={'draft': [('readonly', False)]})
    material_form_id = fields.One2many('disassemble.products.form','disassemble_id','Products to Form',readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', True)]}, index=True, default='New')
    product_id = fields.Many2one('product.template', 'Product',readonly=True, states={'draft': [('readonly', False)]})
    product_product_id = fields.Many2one('product.product', compute='_compute_product_id', string='Product (2)')
    quantity_pro = fields.Integer('Quantity',readonly=True, states={'draft': [('readonly', False)]},default=1)
    date_disassemble = fields.Date('Date',readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
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
        res = {}
        if self.product_id:
            product_ids = self.env['product.product'].search([('product_tmpl_id','=',self.product_id.id)]).ids
            lot_ids = self.env['stock.production.lot'].search([('product_id','in',product_ids)]).ids
            res['domain'] = {'stock_production_prod': [('id','in',lot_ids)]}
            data = []
            for line in self.product_id.material_ids:
                data.append((0, 0, {'product_id': line.product_id.id, 'qty_pro': line.material_quantity * self.quantity_pro}))
            self.material_id = data
        return res

    @api.onchange('material_id')
    @api.depends('material_id.qty_pro')
    def onchange_material_id(self):
        # Calculating the product_data from the materials
        product_data = {}
        for line in self.material_id:
            if line.product_id.id not in product_data:
                product_data.update({line.product_id.id: line.qty_pro})
            else:
                product_data.update({line.product_id.id: line.qty_pro + product_data.get(line.product_id.id)})

        # Find the products that can be formed using the above materials
        product_template_ids = self.env['product.template'].search([('id','!=',self.product_id.id),('material_ids.product_id','in',product_data.keys())])

        result = []
        for template in product_template_ids:
            data, check_list = {}, []
            # Check new product can be formed using the material
            for line in template.material_ids:
                if line.product_id.id in product_data and product_data.get(line.product_id.id) >= line.material_quantity:
                    check_list.append(True)
                    if line.product_id.id not in data:
                        data.update({line.product_id.id: line.material_quantity})
                    else:
                        data.update({line.product_id.id: line.material_quantity + data.get(line.product_id.id)})
                else:
                    check_list.append(False)
            # Check new product can be formed using the materials quantity
            product_ok = False
            product_count = 1
            if all(check_list):
                while(product_count):
                    check_list2 = []
                    for product_id in data:
                        if product_data.get(product_id) >= data.get(product_id) * product_count:
                            check_list2.append(True)
                        else:
                            check_list2.append(False)
                    if all(check_list2):
                        product_ok = True
                        product_count += 1
                        continue
                    else:
                        product_count -= 1
                        break
            # Adding the product to products to form
            if product_ok:
                materials = ''
                for line in template.material_ids:
                    materials += line.product_id.name + ' x '+ str(line.material_quantity) + '\n'
                product_id = self.env['product.product'].search([('product_tmpl_id','=',template.id)])
                if product_id:
                    result.append((0,0,{'product_id': product_id.id, 'materials': materials, 'possible_qty': product_count, 'possible_qty_dynamic': product_count}))
        self.material_form_id = result

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('res.disassemble') or 'New'
        result = super(ResDisassemble, self).create(vals)
        return result

    @api.multi
    def validate_product_to_form(self):
        for record in self:
            # Total materials
            total_product_data = {}
            for line in record.material_id:
                if line.product_id.id not in total_product_data:
                    total_product_data.update({line.product_id.id: line.qty_pro})
                else:
                    total_product_data.update({line.product_id.id: line.qty_pro + total_product_data.get(line.product_id.id)})
            available_product_data = total_product_data.copy()

            # Consumed materials
            consumed_product_data = {}
            for line in record.material_form_id:
                for line2 in line.product_id.material_ids:
                    if line2.product_id.id not in consumed_product_data:
                        consumed_product_data.update({line2.product_id.id: line2.material_quantity * line.quantity})
                    else:
                        consumed_product_data.update({line2.product_id.id: consumed_product_data.get(line2.product_id.id) + (line2.material_quantity * line.quantity)})

            # Available materials
            for product_id in consumed_product_data:
                available_product_data.update({product_id: available_product_data.get(product_id) - consumed_product_data.get(product_id)})

            for product_id in available_product_data:
                if available_product_data.get(product_id) < 0.0:
                    product_obj = self.env['product.product'].sudo().browse(product_id)
                    message = 'Error!\nProducts to Form configuration is incorrect\n\n'
                    message += 'Product            : %s' % product_obj.name
                    message += '\nTotal Materials  : %s' % total_product_data.get(product_id)
                    message += '\nMaterials Needed : %s' % consumed_product_data.get(product_id)
                    message += '\nPlease reconfigure to proceed disassemble.'
                    raise UserError(message)

    @api.multi
    def action_disassemble(self):
        if not self.material_id:
            raise UserError('Can not disassemble without materials')
        if self.quantity_pro > self.product_id.qty_available:
            raise UserError('Quantity greater than the on hand quantity (%s)' % self.product_id.qty_available)
        self.validate_product_to_form()
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
            # Reducing qty of main product
            vals = {
                'product_id': product_obj.id,
                'product_uom_qty': record.quantity_pro,
                'product_uom': product_obj.uom_id.id,
                'name': product_obj.name,
                'date_expected': fields.Datetime.now(),
                'procure_method': 'make_to_stock',
                'location_id': record.location_src_id.id,
                'location_dest_id': dest_location.id,
                'origin': record.name,
                'restrict_lot_id': record.stock_production_prod.id or False,
            }
            move = self.env['stock.move'].create(vals)
            move.action_confirm()
            move.action_done()

            # Processing materials
            for line in record.material_form_id:
                if line.quantity:
                    # reduce material qty in dict
                    for line2 in line.product_id.product_tmpl_id.material_ids:
                        product_data.update({line2.product_id.id: product_data.get(line2.product_id.id) - (line2.material_quantity * line.quantity)})
                    # increase product formed
                    stock_move = {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_id.uom_id.id,
                        'name': line.product_id.name,
                        'date_expected': fields.Datetime.now(),
                        'procure_method': 'make_to_stock',
                        'location_id': dest_location.id,
                        'location_dest_id': record.location_src_id.id,
                        'origin': record.name,
                    }
                    move = self.env['stock.move'].create(stock_move)
                    move.action_confirm()
                    move.action_done()

            # increasing material qty
            for product_id in product_data:
                if product_data.get(product_id):
                    lot_line_id = self.env['disassemble.materials'].search([('disassemble_id','=',record.id),('product_id','=',product_id)])
                    product_obj = self.env['product.product'].browse(product_id)
                    stock_move = {
                        'product_id': product_obj.id,
                        'product_uom_qty': product_data.get(product_id),
                        'product_uom': product_obj.uom_id.id,
                        'name': product_obj.name,
                        'date_expected': fields.Datetime.now(),
                        'procure_method': 'make_to_stock',
                        'location_id': dest_location.id,
                        'location_dest_id': record.location_src_id.id,
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

ResDisassemble()

class DisassembleMaterials(models.Model):
    _name = 'disassemble.materials'

    disassemble_id = fields.Many2one('res.disassemble', 'Materials')
    product_id = fields.Many2one('product.product', 'Product')
    qty_pro = fields.Integer('Quantity')
    stock_lot = fields.Many2one('stock.production.lot', 'Serial Number')

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if self.product_id:
            lot_ids = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)]).ids
            res['domain'] = {'stock_lot': [('id','in',lot_ids)]}
        return res

DisassembleMaterials()

class DisassembleProcuctsForm(models.Model):
    _name = 'disassemble.products.form'

    @api.depends('possible_qty','quantity')
    def compute_possible_qty(self):
        for record in self:
            record.possible_qty_dynamic = record.possible_qty - record.quantity

    disassemble_id = fields.Many2one('res.disassemble', 'Materials')
    product_id = fields.Many2one('product.product', 'Product')
    materials = fields.Text('Materials')
    possible_qty = fields.Integer('Possible Quantity')
    possible_qty_dynamic = fields.Integer(compute='compute_possible_qty', string='Dynamic Possible Quantity')
    quantity = fields.Integer('Quantity')

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {}
        if self.product_id:
            lot_ids = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)]).ids
            res['domain'] = {'stock_lot': [('id','in',lot_ids)]}
        return res

    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.quantity > self.possible_qty:
            self.quantity = 0
            return {
                'warning': {
                    'title': "Warning!",
                    'message': "You can not set more than the possible quantity",
                }
            }

DisassembleProcuctsForm()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    material_ids = fields.One2many('component.materials', 'component_id', string='Disassemble')

    @api.multi
    def disassemble_form_view(self):
        ctx = dict()
        form_id = self.env['ir.model.data'].sudo().get_object_reference('simple_assemble_disassemble', 'res_disassemble_form_view')[1]
        ctx.update({
            'default_product_id': self.id,
        })
        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.disassemble',
            'views': [(form_id, 'form')],
            'view_id': form_id,
            'target': 'new',
            'context': ctx,
        }
        return action

ProductTemplate()

class ComponentMaterials(models.Model):
    _name = 'component.materials'

    component_id = fields.Many2one('product.template', 'Materials')
    product_id = fields.Many2one('product.product', 'Product')
    material_quantity = fields.Integer('Quantity')

ComponentMaterials()