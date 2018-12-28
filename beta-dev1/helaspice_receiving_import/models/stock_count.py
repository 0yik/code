from odoo import models, fields, api

class StockCount(models.Model):
    _name = 'stock.count'
    _inherit = ['mail.thread']
    _description = 'Stock Count'
    _order = 'id desc'

    name = fields.Char('Reference')
    state = fields.Selection([('open', 'Open'), ('cancel', 'Cancelled'), ('in_progress', 'In Progress'), ('close', 'Closed')], copy=False, track_visibility='onchange', default='open', string='Status')
    count_date = fields.Date('Count Date')
    remarks = fields.Text()
    line_ids = fields.One2many('stock.count.line', 'count_id', string='Lines')

    def search_product(self, arg):
        product_id = self.env['product.product'].search([('barcode', '=', str(arg))], limit=1)
        if not product_id:
            product_id = self.env['product.product'].search([('default_code', '=', str(arg))], limit=1)
        product_list = []
        if product_id:
            vals = {}
            vals['product_id'] = product_id.id
            vals['product'] = product_id.name
            vals['item_no'] = product_id.default_code
            vals['barcode'] = product_id.barcode
            vals['rack_location'] = product_id.rack_location
            if product_id.tracking == 'none':
                vals['tracking'] = 'N'
            else:
                vals['tracking'] = 'Y'
            product_list.append(vals)
        else:
            for product_id in self.env['product.product'].search([('name', 'ilike', str(arg))]):
                vals = {}
                vals['product_id'] = product_id.id
                vals['product'] = product_id.name
                vals['item_no'] = product_id.default_code
                vals['barcode'] = product_id.barcode
                vals['rack_location'] = product_id.rack_location
                if product_id.tracking == 'none':
                    vals['tracking'] = 'N'
                else:
                    vals['tracking'] = 'Y'
                product_list.append(vals)
        return product_list

    def search_batch_no(self, product_id, lot_name):
        lot_id = self.env['stock.production.lot'].search([('product_id', '=', int(product_id)), ('name', '=', str(lot_name))], limit=1)
        if lot_id:
            vals = {}
            vals['lot_id'] = lot_id.id
            vals['lot_name'] = lot_id.name
            vals['batch_no'] = lot_id.batch_no if not lot_id.actual_batch_no else lot_id.actual_batch_no
            if lot_id.actual_bbd:
                vals['bbd'] = str(lot_id.actual_bbd)[:10]
            else:
                vals['bbd'] = str(lot_id.use_date)[:10] if lot_id.use_date else ''
            return vals
        return {}

    def stock_count_without_tracking(self, product_id, qty):
        if not product_id or not qty:
            return False
        try:
            vals = {}
            vals['product_id'] = int(product_id)
            vals['qty'] = qty
            self.env['stock.count.quant'].create(vals)
            return True
        except:
            return False

    def update_stock_count(self, product_id, lot_list):
        if not product_id or not lot_list:
            return False
        try:
            for data in lot_list:
                if data.get('qty', 0) > 0 and data.get('lot_name', False):
                    lot_id = self.env['stock.production.lot'].search([('product_id', '=', int(product_id)), ('name', '=', str(data.get('lot_name', '')))], limit=1)
                    if not lot_id:
                        lot_vals = {}
                        lot_vals['product_id'] = int(product_id)
                        lot_vals['name'] = str(data.get('lot_name', ''))
                        if str(data.get('lot_name', '')).lower() != 'false':
                            lot_vals['batch_no'] = str(data.get('batch_no', ''))
                        if str(data.get('bbd', '')).lower() != 'false':
                            lot_vals['use_date'] = str(data.get('bbd', '')) + ' 00:00:00' if data.get('bbd', False) else False
                        lot_id = self.env['stock.production.lot'].create(lot_vals)
                    vals = {}
                    vals['product_id'] = int(product_id)
                    vals['lot_id'] = lot_id.id
                    vals['qty'] = data.get('qty')
                    self.env['stock.count.quant'].create(vals)
            return True
        except:
            return False

    def action_inprogress(self):
        self.write({'state': 'inprogress'})
    
    def action_done(self):
        self.write({'state': 'close'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
    
    def log_a_note(self, note):
        self.ensure_one()
        if note.strip():
            self.write({'remarks': note.strip()})
            self.message_post('<b>Remarks:</b><ul><li>%s.</li></ul>'% note.strip())
        else:
            self.write({'remarks': False})
        return True

StockCount()

class StockCountLine(models.Model):
    _name = 'stock.count.line'
    _description = 'Stock Count Lines'

    @api.depends('quant_ids', 'quant_ids.qty', 'quant_ids.lot_id')
    def compute_existing_qty(self):
        for record in self:
            if record.state != 'close':
                record.existing_qty = sum([x.qty for x in record.quant_ids])

    @api.depends('count_lot_ids', 'count_lot_ids.qty', 'count_lot_ids.lot_id')
    def compute_count_qty(self):
        for record in self:
                record.count_qty = sum([x.qty for x in record.count_lot_ids])

    def _get_stock_quant(self):
        for record in self:
            if record.product_id:
                quant_ids = self.env['stock.quant'].search([('product_id', '=', record.product_id.id), ('lot_id', '!=', False)]).ids
            else:
                quant_ids = []
            record.quant_ids = [(6, 0, quant_ids)]

    @api.depends('count_id.state')
    def get_count_state(self):
        for record in self:
            record.state = record.count_id.state if record.count_id else False

    def get_tracking(self):
        for record in self:
            if record.product_id:
                record.tracking = record.product_id.tracking

    count_id = fields.Many2one('stock.count', string='Stock Count')
    state = fields.Char(compute='get_count_state', store=True, string='Status')
    product_id = fields.Many2one('product.product', required=True, string='Product')
    qty = fields.Float(string='SAP Quantity')
    existing_qty = fields.Float(compute='compute_existing_qty', store=True, string='Existing Qty')
    quant_ids = fields.Many2many('stock.quant', compute='_get_stock_quant', string='Quants')
    count_qty = fields.Float(compute='compute_count_qty', string='Warehouse Quantity')
    count_lot_ids = fields.Many2many('stock.count.quant', string='Lot/Serial Nos')
    tracking = fields.Char(compute='get_tracking', string='Tracking')

    def find_lot_number(self, lot_name):
        self.ensure_one()
        lot_id = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', '=', lot_name)], limit=1)
        if lot_id:
            vals = {}
            vals['lot_name'] = lot_id.name
            vals['batch_no'] = lot_id.batch_no if not lot_id.actual_batch_no else lot_id.actual_batch_no
            vals['bbd'] = str(lot_id.use_date)[:10] if lot_id.use_date else ''
            return vals
        else:
            return {}

    def view_existing_data(self):
        return {
            'name': 'Lot/Serial Numbers',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env['ir.model.data'].xmlid_to_res_id('helaspice_receiving_import.stock_count_lot_form'),
            'res_model': 'stock.count.line',
            'target': 'new',
            'res_id': self.ids[0],
        }

    def view_count_data(self):
        return {
            'name': 'Lot/Serial Numbers',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env['ir.model.data'].xmlid_to_res_id('helaspice_receiving_import.stock_count_lot_form2'),
            'res_model': 'stock.count.line',
            'target': 'new',
            'res_id': self.ids[0],
        }

    @api.multi
    def save(self):
        return {'type': 'ir.actions.act_window_close'}

StockCountLine()

class StockCountLot(models.Model):
    _name = 'stock.count.lot'
    _description = 'Stock Count Lot'

    line_id = fields.Many2one('stock.count.line', string='Count Line')
    lot_id = fields.Many2one('stock.production.lot', required=False, string='Lot/Serial No')
    qty = fields.Float()

StockCountLot()

class StockCountQuant(models.Model):
    _name = 'stock.count.quant'
    _description = 'Stock Count Quant'
    _rec_name = 'product_id'
    _order = 'id desc'

    @api.depends('lot_id', 'lot_id.use_date', 'lot_id.actual_bbd', 'lot_id.batch_no', 'lot_id.actual_batch_no')
    def compute_batch_bbd(self):
        for record in self:
            lot_id = record.lot_id
            if lot_id:
                record.use_date = lot_id.use_date if lot_id.use_date else lot_id.actual_bbd
                record.batch_no = lot_id.batch_no if lot_id.batch_no else lot_id.actual_batch_no
            else:
                record.use_date = False
                record.batch_no = False

    product_id = fields.Many2one('product.product', required=True, string='Product')
    lot_id = fields.Many2one('stock.production.lot', required=False, string='Lot/Serial No')
    use_date = fields.Datetime(compute='compute_batch_bbd', string='Best Before Date')
    batch_no = fields.Char(compute='compute_batch_bbd', string='Batch No')
    qty = fields.Float()
    is_closed = fields.Boolean()

    @api.model
    def create(self, vals):
        record = super(StockCountQuant, self).create(vals)
        for line in self.env['stock.count.line'].search([('state', '=', 'open'), ('product_id', '=', record.product_id.id if record.product_id else False)]):
            line.write({'count_lot_ids': [(4, record.id)]})
        return record

StockCountQuant()