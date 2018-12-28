from odoo import api, fields, models, _


class InventoryRequest(models.Model):
    _name = 'inventory.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'mail.activity.mixin' ]  # use for send mail and chater message

    name = fields.Char('Number', readonly=True, index=True, default=lambda self: _('New'), copy=False)
    # partner_id = fields.Many2one('res.partner', 'Partner', required=False,
    #                              default=lambda self: self.env.user.partner_id.id)
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
    to_dos = fields.Many2many('mail.activity')

    @api.model
    def default_get(self, fields):
        res = super(InventoryRequest, self).default_get(fields)
        if not res.get('location_id',False):
            res['location_id'] = self.env['res.branch'].sudo().search([('name','=','Central')],limit=1).location_id.id
        if not res.get('location_dest_id',False):
            res['location_dest_id'] = self.env.user.branch_id.location_id.id
        if not res.get('picking_type_id',False):
            res['picking_type_id'] = self.env['res.branch'].sudo().search([('name', '=', 'Central')], limit=1).warehouse_id.int_type_id.id
        return res

    @api.multi
    def _has_approval(self):
        for record in self:
            users = self.env.ref('sarangoci_stock_inventory_request.group_inventory_supervisor').users.filtered(lambda u: u.branch_id.id==record.create_uid.branch_id.id)
            print "V  usersusersusers   ",users,record.create_uid,record.create_uid.branch_id,self.env.user.branch_id
            if record.state == "tobeapproved" and self.env.user in users:
                record.approval_access = True


    @api.multi
    def btn_to_be_approval(self):
        for inv_record in self:
            supervisors = self.env.ref('sarangoci_stock_inventory_request.group_inventory_supervisor').users.filtered(lambda u: u.branch_id.id==inv_record.create_uid.branch_id.id)
            email_from = self.env.user.login
            vals = {
            'summary': 'Approve Inventory Request '+inv_record.name,
            'icon': "fa-dolly-flatbed-alt",
            'res_model_id': self.env['ir.model'].search([('name', '=', inv_record._name)]).id,
            'res_id':inv_record.id,
            'res_name': inv_record.name,
            }
            to_dos = []
            for supervisor in supervisors:
                vals['user_id'] = supervisor.id
                vals['note'] =  """
                <html>
                    <head>
                        Dear %s,
                    </head>
                    <body>
                        You have <b>an inventory request</b> waiting for your approval.<br/>
                        Please Go to Document.<br/><br/>
                        Requestor : %s. <br/>
                        <strong>Thank You</strong>
                    </body>
                <html>
            """% (
                supervisor.name, self.env.user.name)
                to_dos.append(self.env['mail.activity'].sudo().create(vals).id)
            inv_record.write({'state': 'tobeapproved', 'to_dos': [(6, 0, to_dos)]})

    @api.multi
    def btn_approved(self):
        self.state = 'approved'
        for to_do in self.to_dos:
            to_do.action_feedback(feedback="Inventory Request is approved by "+ self.env.user.name)

    @api.multi
    def btn_rejected(self):
        self.state = 'rejected'
        for to_do in self.to_dos:
            to_do.action_feedback(feedback="Inventory Request is rejected by "+ self.env.user.name)

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

    @api.model
    def get_warehouse_user(self):
        if self._uid:
            return self.env.user.branch_id.location_id.id

    inventory_request_id = fields.Many2one('inventory.request', string="Inventory Request")  # o2m
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_code = fields.Char(string="Product Code")
    product_uom_id = fields.Many2one('product.uom', string="Unit of Measure")
    product_qty = fields.Char(string='Product Qty', required=True)
    location_id = fields.Many2one('stock.location', string='Warehouse',readonly=True,default=get_warehouse_user)
    last_purchase_history = fields.Char(string='Last Request History', readonly=True)
    last_purchase_qty = fields.Char(string='Last Request Qty', readonly=True)
    # stock_current_toko = fields.Char(string='Stock Current Toko', readonly=True)  # Type Shop current quantity
    # stock_display_toko = fields.Char(string='Stock Display Toko',
    #                                  readonly=True)  # Type Shop reordering minimum quantity
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
        # reodering min qty is not shop
        # is_not_shop standard_qty_warehouse
        warehouse_orderpoint_is_not_shop = self.product_id.orderpoint_ids.filtered(lambda a: a.location_id.is_shop != True and a.location_id.id == self.location_id.id)
        is_not_shop_list = warehouse_orderpoint_is_not_shop.mapped('id')
        standard_qty_warehouse_value = warehouse_orderpoint_is_not_shop.search([('id', 'in', is_not_shop_list)],
                                                                               limit=1, order='id desc')
        # get record to stock_quant
        stock_quant_records = self.env['stock.quant'].search([('product_id', '=', self.product_id.id)])
        # sum of is store and not store of qty
        # current_current_toko = sum(stock_quant_records.filtered(lambda a: a.location_id.is_shop == True).mapped('qty'))
        # current_current_toko = self.product_id.qty_available
        # current_current_gudang = sum(stock_quant_records.filtered(lambda a: a.location_id.is_shop != True).mapped('qty'))
        current_current_gudang = sum(stock_quant_records.filtered(lambda a: a.location_id.id == self.location_id.id).mapped('qty'))
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
            res['domain'] = {'location_id': [('id', 'in', location_id), ('usage', '=', 'internal')]}

        self.last_purchase_history = last_inventory_request_record.min_date
        self.last_purchase_qty = product_qty
        # self.stock_display_toko = standard_qty_shop_value.product_min_qty
        self.stock_display_gudang = standard_qty_warehouse_value.product_min_qty
        # self.stock_current_toko = current_current_toko
        self.stock_current_gudang = current_current_gudang
        self.sale_order_reference_lines = line
        self.product_uom_id = self.product_id.uom_id.id
        return res
