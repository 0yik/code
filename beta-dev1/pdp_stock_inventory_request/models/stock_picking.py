from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            product_record = self.env['product.product'].browse(vals['product_id'])
            ref = product_record.default_code
            name = '[' + ref + ']' + ' ' + product_record.name if ref else product_record.name
            vals['name'] = name
        res = super(StockMove, self).create(vals)
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #code = fields.Char(string='Product Code')
    request_type = fields.Selection([
        ('inventory_request', 'Inventory Request'), ('return_request', 'Return Request'),
        ('tester_request', 'Tester Request')], string='Request Type')
    inventory_request_id = fields.Many2one('inventory.request', string='Request No.')#custom field
    return_request_id = fields.Many2one('return.request', string='Request No.', invisible = True)  # custom field
    tester_request_id = fields.Many2one('tester.request', string='Request No.', invisible = True)  # custom field
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'), ('inprogess', 'In Progress'), ('done', 'Done')], string='Status',
        compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")
    inventory_request_load_data = fields.Boolean(string="Inventory Request")
    return_request_load_data = fields.Boolean(string="Return Request")
    tester_request_load_data = fields.Boolean(string="Tester Request")

    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        if not self.request_type:
            location = self.env.ref('stock.stock_location_stock')
            self.location_src_id = self.picking_type_id.default_location_src_id.id or location.id
            self.location_dest_id = self.picking_type_id.default_location_dest_id.id or location.id

    # @api.multi
    # @api.onchange('request_type')
    # def onchange_request_type(self):
    #     self.location_dest_id = ''
    #     self.location_id = ''
    #     self.min_date = ''
    #     self.inventory_request_id = ''
    #     self.return_request_id = ''
    #     self.tester_request_id = ''
    #     self.move_lines = ''

        #self.env['stock.picking.type'].search([('name', '=', self.inventory_request_id.id)])
        #self.picking_type_id =


    @api.multi
    @api.depends('move_lines.date_expected')
    def _compute_dates(self):
        for picking in self:
            if picking.inventory_request_id:
                picking.min_date = picking.inventory_request_id.min_date
            elif picking.return_request_id:
                picking.min_date = picking.return_request_id.min_date
            elif picking.tester_request_id:
                picking.min_date = picking.tester_request_id.min_date
            else:
                picking.min_date = min(picking.move_lines.mapped('date_expected') or [False])
                picking.max_date = max(picking.move_lines.mapped('date_expected') or [False])


    @api.multi
    @api.onchange('inventory_request_id')
    def onchange_inventory_request_id(self):
        if self.inventory_request_id:
            self.location_id = self.inventory_request_id.location_id.id
            self.location_dest_id = self.inventory_request_id.location_dest_id.id
            self.partner_id = self.inventory_request_id.partner_id.id
            self.min_date = self.inventory_request_id.min_date
            self.picking_type_id = self.inventory_request_id.picking_type_id
            # self.move_lines = ''
            name = []
            inventory_request_records = self.env['stock.picking'].search([('inventory_request_id', '=', self.inventory_request_id.id)])
            if inventory_request_records:
                for stock_picking_record in inventory_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        name.append(str(stock_picking_record.name))
                        #if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                        if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                            raise UserError(_("Inventory Request No.:-%s allready used in %s")% (self.inventory_request_id.name, stock_picking_record.name))
                        #raise UserError(_("Inventory Request No.:-%s allready used in %s") % (self.inventory_request_id.name, name))



    @api.multi
    def inventory_request_load_data(self):
        if self.picking_type_id:
            if self.move_lines:
                self.move_lines.unlink()
            move_lines = []
            for inventory_request_line in self.inventory_request_id.inventory_request_lines:
                code = ''
                if inventory_request_line.product_id.code:
                    code = inventory_request_line.product_code
                uom_categ_id = self.env.ref('product.product_uom_categ_kgm').id
                weight_uom_id = self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)],limit=1)
                move_lines.append((0, 0, {
                    'code': str(code),
                    'name': inventory_request_line.product_id.partner_ref,
                    'product_id': inventory_request_line.product_id.id,
                    'product_uom_qty': float(inventory_request_line.product_qty),
                    'product_uom': inventory_request_line.product_uom_id.id,
                    'state': self.state,
                    'location_id': self.inventory_request_id.location_id.id,
                    'location_dest_id': self.inventory_request_id.location_dest_id.id,
                    'date_expected': self.inventory_request_id.min_date,
                    'picking_type_id': self.picking_type_id.id,  # new
                    'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'company_id': self.partner_id.company_id.id,  # default
                    'procure_method': 'make_to_stock',  # default
                    'weight_uom_id': weight_uom_id.id,  # default

                }))
            self.update({
                'move_lines': move_lines,
            })
            inventory_request_load_data = True
        return True


    @api.multi
    @api.onchange('return_request_id')
    def onchange_return_request_id(self):
        if self.return_request_id:
            self.location_id = self.return_request_id.location_id.id
            self.location_dest_id = self.return_request_id.location_dest_id.id
            self.partner_id = self.return_request_id.partner_id.id
            self.min_date = self.return_request_id.min_date
            self.picking_type_id = self.return_request_id.picking_type_id
            # self.move_lines = ''
            name = []
            return_request_records = self.env['stock.picking'].search([('return_request_id', '=', self.return_request_id.id)])
            if return_request_records:
                for stock_picking_record in return_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        name.append(str(stock_picking_record.name))
                        if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                            raise UserError(_("Return Request No.:-%s allready used in %s")% (self.return_request_id.name, stock_picking_record.name))
                        #raise UserError(_("Return Request No.:-%s allready used in %s") % (self.return_request_id.name, name))


    @api.multi
    def return_request_load_data(self):
        if self.picking_type_id:
            if self.move_lines:
                self.move_lines.unlink()
            move_lines = []
            for return_request_line in self.return_request_id.return_request_lines:
                code = ''
                if return_request_line.product_id.code:
                    code = return_request_line.product_code
                uom_categ_id = self.env.ref('product.product_uom_categ_kgm').id
                weight_uom_id = self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1)
                move_lines.append((0, 0, {
                    'code': str(code),
                    'name': return_request_line.product_id.partner_ref,
                    'product_id': return_request_line.product_id.id,
                    'product_uom_qty': float(return_request_line.product_qty),
                    'product_uom': return_request_line.product_uom_id.id,
                    'state': self.state,
                    'location_id': self.return_request_id.location_id.id,
                    'location_dest_id': self.return_request_id.location_dest_id.id,
                    'date_expected': self.return_request_id.min_date,
                    'picking_type_id': self.picking_type_id.id,  # new
                    'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'company_id': self.partner_id.company_id.id,  # default
                    'procure_method': 'make_to_stock',  # default
                    'weight_uom_id': weight_uom_id.id,  # default
                }))
            self.update({
                'move_lines': move_lines,
            })
        return True


    @api.multi
    @api.onchange('tester_request_id')
    def onchange_tester_request_id(self):
        if self.tester_request_id:
            self.location_id = self.tester_request_id.location_id.id
            self.location_dest_id = self.tester_request_id.location_dest_id.id
            self.partner_id = self.tester_request_id.partner_id.id
            self.min_date = self.tester_request_id.min_date
            self.picking_type_id = self.tester_request_id.picking_type_id
            # self.move_lines = ''
            name = []
            tester_request_records = self.env['stock.picking'].search([('tester_request_id', '=', self.tester_request_id.id)])
            if tester_request_records:
                for stock_picking_record in tester_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        name.append(str(stock_picking_record.name))
                        if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                            raise UserError(_("Tester Request No.:-%s allready used in %s")% (self.tester_request_id.name, stock_picking_record.name))
                        # raise UserError(_("Tester Request No.:-%s allready used in %s") % (self.tester_request_id.name, name))

    @api.multi
    def tester_request_load_data(self):
        if self.picking_type_id:
            if self.move_lines:
                self.move_lines.unlink()
            move_lines = []
            for tester_request_line in self.tester_request_id.tester_request_lines:
                code = ''
                if tester_request_line.product_id.code:
                    code = tester_request_line.product_code
                uom_categ_id = self.env.ref('product.product_uom_categ_kgm').id
                weight_uom_id = self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1)
                move_lines.append((0, 0, {
                    'code': str(code),
                    'name': tester_request_line.product_id.partner_ref,
                    'product_id': tester_request_line.product_id.id,
                    'product_uom_qty': float(tester_request_line.product_qty),
                    'product_uom': tester_request_line.product_uom_id.id,
                    'state': self.state,
                    'location_id': self.tester_request_id.location_id.id,
                    'location_dest_id': self.tester_request_id.location_dest_id.id,
                    'date_expected': self.tester_request_id.min_date,
                    'picking_type_id': self.picking_type_id.id,  # new
                    'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'company_id': self.partner_id.company_id.id,  # default
                    'procure_method': 'make_to_stock',  # default
                    'weight_uom_id': weight_uom_id.id,  # default
                }))
            self.update({
                'move_lines': move_lines,
            })
        return True

    @api.model
    def create(self, vals):
        inventory_request_id = vals.get('inventory_request_id')
        return_request_id = vals.get('return_request_id')
        tester_request_id = vals.get('tester_request_id')
        if inventory_request_id:
            inventory_request_records = self.env['stock.picking'].search([('inventory_request_id', '=', vals.get('inventory_request_id'))])
            if inventory_request_records:
                for stock_picking_record in inventory_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        if not vals.get('backorder_id'):
                            if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                                raise UserError(_("Inventory Request No. allready used"))

        elif return_request_id:
            return_request_records = self.env['stock.picking'].search([('return_request_id', '=', vals.get('return_request_id'))])
            if return_request_records:
                for stock_picking_record in return_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        if not vals.get('backorder_id'):
                            if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                                raise UserError(_("Return Request No. allready used "))
                        '''else:
                            vals.get('return_request_id') = return_request_id'''

        elif tester_request_id:
            tester_request_records = self.env['stock.picking'].search(
                [('tester_request_id', '=', vals.get('tester_request_id'))])
            if tester_request_records:
                for stock_picking_record in tester_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        if not vals.get('backorder_id'):
                            if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                                raise UserError(_("Tester Request No. allready used"))

        return super(StockPicking, self).create(vals)

    @api.multi
    def write(self, vals):
        inventory_request_id = vals.get('inventory_request_id')
        return_request_id = vals.get('return_request_id')
        tester_request_id = vals.get('tester_request_id')
        if inventory_request_id:
            inventory_request_records = self.env['stock.picking'].search([('inventory_request_id', '=', vals.get('inventory_request_id'))])
            if inventory_request_records:
                for stock_picking_record in inventory_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        if not vals.get('backorder_id'):
                            if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                                raise UserError(_("Inventory Request No. allready used"))
        elif return_request_id:
            return_request_records = self.env['stock.picking'].search(
                [('return_request_id', '=', vals.get('return_request_id'))])
            if return_request_records:
                for stock_picking_record in return_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        if not vals.get('backorder_id'):
                            if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                                raise UserError(_("Return Request No. allready used "))
        elif tester_request_id:
            tester_request_records = self.env['stock.picking'].search(
                [('tester_request_id', '=', vals.get('tester_request_id'))])
            if tester_request_records:
                for stock_picking_record in tester_request_records:
                    for pack_operation_product_record in stock_picking_record.pack_operation_product_ids:
                        if not vals.get('backorder_id'):
                            if pack_operation_product_record.product_qty == pack_operation_product_record.qty_done:
                                raise UserError(_("Tester Request No. allready used"))

        return super(StockPicking, self).write(vals)

    @api.model
    def default_get(self, fields):
        rec = super(StockPicking, self).default_get(fields)
        rec['partner_id'] = self.env.user.partner_id.id
        return rec


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def write(self, vals):
        res = super(StockPackOperation, self).write(vals)
        # stock_picking = self.env['stock.picking'].search([('pack_operation_product_ids', 'in', self.id)])
        stock_picking = self.env['stock.picking'].browse(self.picking_id.id)
        if stock_picking.pack_operation_product_ids:
            for pack_operation_product_record in stock_picking.pack_operation_product_ids:
                if pack_operation_product_record.qty_done != 0:
                    if pack_operation_product_record.qty_done < pack_operation_product_record.product_qty:
                        stock_picking.state = 'inprogess'

        return res
