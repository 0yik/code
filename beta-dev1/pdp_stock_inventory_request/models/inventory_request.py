from odoo import api, fields, models, _


class InventoryRequest(models.Model):
    _name = 'inventory.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin', ]  # use for send mail and chater message

    name = fields.Char('Number', readonly=True, index=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True,
                                 default=lambda self: self.env.user.partner_id.id)
    location_id = fields.Many2one('stock.location', "Source Location Zone", required=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location Zone", required=True)
    min_date = fields.Datetime('Scheduled Date', required=True)
    origin = fields.Char('Source Document')
    user_id = fields.Many2one('res.users', "Approver")
    approval_access = fields.Boolean(compute="_has_approval",string="Has Approval")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('tobeapproved', 'To be approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="state", default='draft', readonly=True)
    inventory_request_lines = fields.One2many('inventory.request.line', 'inventory_request_id', 'Inventory Detail',
                                              domain=[('product_id', '!=', False)])

    @api.multi
    @api.depends('user_id')
    def _has_approval(self):
        for record in self:
            if record.user_id.id == self.env.user.id:
                if record.state == "tobeapproved":
                    record.approval_access = True


    @api.multi
    def btn_to_be_approval(self):
        for inv_record in self:
            mail_vals = {}
            if inv_record.user_id:
                partner_id = self.env['res.partner'].sudo().browse(inv_record.user_id.partner_id.id)
                email_from = self.env.user.login
                subject = 'You have on inventory request to approve'
                message = """
                                    <html>
                                        <head>
                                            Dear %s,
                                        </head>
                                        <body>
                                            You have <b>an inventory request (<a href=# data-oe-model=inventory.request data-oe-id=%d>%s</a>)</b> waiting for your approval.<br/><br/>
                                            Requestor : %s. <br/>
                                            <strong>Thank You</strong>
                                        </body>
                                    <html>""" % (
                inv_record.user_id.name, inv_record.id, inv_record.name, inv_record.partner_id.name)
                mail_vals['subject'] = subject
                #mail_vals['res_id'] = inv_record.id
                #mail_vals['model'] = inv_record._name
                mail_vals['body'] = '<pre>%s</pre>' % message
                mail_vals['email_from'] = email_from
                mail_vals['partner_ids'] = [(6, 0, [partner_id.id])],
                mail_vals['needaction_partner_ids'] = [(6, 0, [partner_id.id])]
                thread_pool = self.env['mail.message'].create(mail_vals)
                abc = thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
                inv_record.write({'state': 'tobeapproved'})

    @api.multi
    def btn_approved(self):
        self.state = 'approved'

    @api.multi
    def btn_rejected(self):
        self.state = 'rejected'

   

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('inventory.request')
        result = super(InventoryRequest, self).create(vals)
        return result


class SaleOrderReference(models.Model):
    _name = 'sale.order.reference'
    _rec_name = 'so_number'

    so_number = fields.Char(string='Sale Order', readonly=True)
    so_date = fields.Char(string='Date', readonly=True)
    so_quantity = fields.Char(string='Quantity', readonly=True)
    inventory_request_line_id = fields.Many2one('inventory.request.line', string='Inventory Request Product')  # o2m


class InventoryRequestLine(models.Model):
    _name = 'inventory.request.line'
    _rec_name = 'product_id'

    inventory_request_id = fields.Many2one('inventory.request', string="Inventory Request")  # o2m
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_code = fields.Char(string="Product Code")
    product_uom_id = fields.Many2one('product.uom', string="Unit of Measure")
    product_qty = fields.Char(string='Product Qty', required=True)
    location_id = fields.Many2one('stock.location', string='Warehouse')
    location_id2 = fields.Many2one('stock.location', string='Shop',domain=[('is_shop','=',True),('usage', '=', 'internal')])
    last_purchase_history = fields.Char(string='Last Request History', readonly=True)
    last_purchase_qty = fields.Char(string='Last Request Qty', readonly=True)
    stock_current_toko = fields.Char(string='Stock Current Toko', readonly=True)  # Type Shop current quantity
    stock_display_toko = fields.Char(string='Stock Display Toko',
                                     readonly=True)  # Type Shop reordering minimum quantity
    stock_current_gudang = fields.Char(string='Stock Current Gudang', readonly=True)  # Type not Shop current quantity
    stock_display_gudang = fields.Char(string='Stock Display Gudang',
                                       readonly=True)  # Type not Shop reordering minimum quantity
    sale_order_reference_lines = fields.One2many('sale.order.reference', 'inventory_request_line_id',
                                                 'Sale Order Detail')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        product_record = self.env['product.product'].browse(self.product_id.id)
        if product_record.code:
            self.product_code = product_record.code
        else:
            self.product_code = ''
        # purchase history
        last_inventory_request_lines = self.env['inventory.request.line'].search(
            [('product_id', '=', self.product_id.id)])
        last_inventory_request_lines_ids = last_inventory_request_lines.mapped('id')
        last_inventory_request_record = self.env['inventory.request'].search(
            [('inventory_request_lines', 'in', last_inventory_request_lines_ids)], limit=1, order='id desc')

        product_qty = 0
        for return_request_line in last_inventory_request_record.inventory_request_lines:
            if return_request_line.product_id.id == self.product_id.id:
                product_qty = return_request_line.product_qty

        # reodering min qty is shop
        # is_shop standard_qty_shop_value
        warehouse_orderpoint_is_shop = self.product_id.orderpoint_ids.filtered(lambda a: a.location_id.is_shop == True)
        is_shop_list = warehouse_orderpoint_is_shop.mapped('id')
        # standard_qty_shop_value = warehouse_orderpoint_is_shop.search([('id', 'in', is_shop_list)], limit=1,order='id desc')
        reordering_rule_shop = warehouse_orderpoint_is_shop.filtered(lambda b: b.location_id.id in self.location_id2.ids)
        standard_qty_shop_value = warehouse_orderpoint_is_shop.search([('id', 'in', reordering_rule_shop.ids)], limit=1,order='id desc')
        # reodering min qty is not shop
        # is_not_shop standard_qty_warehouse
        warehouse_orderpoint_is_not_shop = self.product_id.orderpoint_ids.filtered(
            lambda a: a.location_id.is_shop != True)
        is_not_shop_list = warehouse_orderpoint_is_not_shop.mapped('id')
        standard_qty_warehouse_value = warehouse_orderpoint_is_not_shop.search([('id', 'in', is_not_shop_list)],
                                                                               limit=1, order='id desc')
        # get record to stock_quant
        stock_quant_records = self.env['stock.quant'].search([('product_id', '=', self.product_id.id)])
        # sum of is store and not store of qty
        # current_current_toko = sum(stock_quant_records.filtered(lambda a: a.location_id.is_shop == True).mapped('qty'))
        current_current_toko = self.product_id.qty_available
        current_current_gudang = sum(
            stock_quant_records.filtered(lambda a: a.location_id.is_shop != True).mapped('qty'))
        # use domain to location id for selected product
        location_records = stock_quant_records.mapped('location_id')
        location_id = location_records.mapped('id')
        # use product to search in sale
        sale_order_lines_records = self.env['sale.order.line'].search([('product_id', '=', self.product_id.id)])
        sale_order_lines_id = sale_order_lines_records.mapped('id')
        sale_order_ids = []
        line = []
        vals = {}
        so_name = []
        so_quantity = 0
        product = self.product_id.id
        if sale_order_lines_id:
            sale_order_records = self.env['sale.order'].search([('order_line', 'in', sale_order_lines_id)])
            sale_order_ids = sale_order_records.mapped('id')
            for sale_order_record in sale_order_records:
                for order_line in sale_order_record.order_line:
                    if order_line.product_id.id == product:
                        if sale_order_record.name in so_name:
                            so_quantity += order_line.product_uom_qty
                            vals.update({'so_quantity': so_quantity})
                        else:
                            so_quantity = order_line.product_uom_qty
                            vals = {'so_number': sale_order_record.name,
                                    'so_date': sale_order_record.date_order,
                                    'so_quantity': so_quantity
                                    }
                            so_name.append(sale_order_record.name)
                            line.append((0, 0, vals))
        res = {}
        if location_id:
            # res['domain'] = {'location_id': [('id', 'in', location_id), ('usage', '=', 'internal')]}
            res['domain'] = {'location_id': [('id', 'in',location_records.filtered(lambda a:a.is_shop != True).ids), ('usage', '=', 'internal')],'location_id2': [('id', 'in', location_records.filtered(lambda a:a.is_shop == True).ids), ('usage', '=', 'internal')]}

        self.last_purchase_history = last_inventory_request_record.min_date
        self.last_purchase_qty = product_qty
        # self.stock_display_toko = standard_qty_shop_value.product_min_qty
        # self.stock_display_gudang = standard_qty_warehouse_value.product_min_qty
        # self.stock_current_toko = current_current_toko
        # self.stock_current_gudang = current_current_gudang
        self.sale_order_reference_lines = line
        self.product_uom_id = self.product_id.uom_id.id
        return res

    @api.onchange('location_id2')
    def shop_toko_display(self):
        if self.location_id2 and self.product_id:
            self.stock_display_toko = self.env['stock.warehouse.orderpoint'].search([('product_id','=',self.product_id.id),('location_id','=',self.location_id2.id)],limit=1,order='id desc').product_min_qty or 0
            self.stock_current_toko = sum(self.env['stock.quant'].search([('product_id','=',self.product_id.id),('location_id','=',self.location_id2.id)]).mapped('qty')) or 0

    @api.onchange('location_id')
    def warehouse_gudang_display(self):
        if self.location_id and self.product_id:
            self.stock_display_gudang = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id)], limit=1,order='id desc').product_min_qty or 0
            self.stock_current_gudang = sum(self.env['stock.quant'].search([('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id)]).mapped('qty')) or 0
