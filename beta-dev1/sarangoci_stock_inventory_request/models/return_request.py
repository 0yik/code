from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ReturnRequest(models.Model):
    _name = 'return.request'

    name = fields.Char('Number', readonly=True, index=True, default=lambda self: _('New'), copy=False)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True,
                                 default=lambda self: self.env.user.partner_id.id)
    location_id = fields.Many2one('stock.location', "Source Location Zone", required=True)
    location_dest_id = fields.Many2one('stock.location', "Destination Location Zone", required=True)
    min_date = fields.Datetime('Scheduled Date', required=True)
    origin = fields.Char('Source Document')
    new_user_id = fields.Many2one('res.users', "Approver 1")
    user_id = fields.Many2one('res.users', "Approver 2")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('tobeapproved', 'To be approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string="state", default='draft', readonly=True)
    return_request_lines = fields.One2many('return.request.line', 'return_request_id', 'Request Return',
                                           domain=[('product_id', '!=', False)])

    @api.multi
    @api.onchange('user_id')
    def onchange_name(self):
        if not self.new_user_id:
            raise UserError(_("First Approver 1 must be want to approve it then you approve it"))

    @api.multi
    def btn_to_be_approval(self):
        for return_record in self:
            mail_vals = {}
            if return_record.user_id and return_record.new_user_id:
                partner_id = self.env['res.partner'].sudo().browse(return_record.user_id.partner_id.id)
                email_from = self.env.user.login
                subject = 'You have on return request to approve'
                message = """
                                    <html>
                                        <head>
                                            Dear %s,
                                        </head>
                                        <body>
                                            You have <b>a return request (<a href=# data-oe-model=return.request data-oe-id=%d>%s</a>)</b> waiting for your approval.<br/><br/>
                                            Requestor : %s. <br/>
                                            <strong>Thank You</strong>
                                        </body>
                                    <html>""" % (
                return_record.user_id.name, return_record.id, return_record.name, return_record.partner_id.name)
                # mail_message_values = {'res_id': account_payment_id.id,
                #                        'model': account_payment_id._name,
                #                        'message_type': 'notification',
                #                        'body': body,
                #                        'date': datetime.now(), }
                mail_vals['subject'] = subject
                #mail_vals['res_id'] = return_record.id
                #mail_vals['model'] = return_record._name
                mail_vals['body'] = '<pre>%s</pre>' % message
                mail_vals['email_from'] = email_from
                mail_vals['partner_ids'] = [(6, 0, [partner_id.id])],
                mail_vals['needaction_partner_ids'] = [(6, 0, [partner_id.id])]
                thread_pool = self.env['mail.message'].create(mail_vals)
                abc = thread_pool.needaction_partner_ids = [(6, 0, [partner_id.id])]
                #order.send_email()
                return_record.write({'state': 'tobeapproved'})

    @api.multi
    def btn_approved(self):
        self.state = 'approved'

    @api.multi
    def btn_rejected(self):
        self.state = 'rejected'

    

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('return.request')
        result = super(ReturnRequest, self).create(vals)
        return result


class ReturnRequestLine(models.Model):
    _name = 'return.request.line'

    return_request_id = fields.Many2one('return.request', string="Return Request")  # o2m
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_code = fields.Char(string="Product Code", readonly=True)
    product_uom_id = fields.Many2one('product.uom', string="Unit of Measure")
    location_id = fields.Many2one('stock.location', string='Warehouse')
    last_request_qty = fields.Char(string='Last Request Qty', readonly=True, store=True)
    product_qty = fields.Float(string='Product Qty', required=True)
    last_request_date = fields.Char(string='Last Request Date', readonly=True, store=True)
    stock_current_toko = fields.Char(string='Stock Current Toko', readonly=True,
                                     store=True)  # Type Shop current quantity
    stock_display_toko = fields.Char(string='Stock Display Toko', readonly=True,
                                     store=True)  # Type Shop reordering minimum quantity
    return_type = fields.Selection([('expired', 'Expired'),
                                    ('over_stock', 'Over Stock'),
                                    ('discontinue', 'Discontinue')], string='Return Type', required=True)

    @api.multi
    @api.onchange('product_qty')
    def product_qty_change(self):
        if self.product_id.qty_available < self.product_qty:
            raise UserError(
                _(' %s has only %s Quantity Available.') % (self.product_id.name, self.product_id.qty_available))
        return

    @api.multi
    @api.onchange('product_id')
    def return_request_product_id_change(self):
        product_record = self.env['product.product'].browse(self.product_id.id)
        if product_record.code:
            self.product_code = product_record.code
        else:
            self.product_code = ''
        # return history
        last_return_request_lines = self.env['return.request.line'].search([('product_id', '=', self.product_id.id)])
        last_return_request_lines_id = last_return_request_lines.mapped('id')
        last_return_request_record = self.env['return.request'].search(
            [('return_request_lines', 'in', last_return_request_lines_id)], limit=1, order='id desc')
        product_qty = 0
        for return_request_line in last_return_request_record.return_request_lines:
            if return_request_line.product_id.id == self.product_id.id:
                product_qty = return_request_line.product_qty
        # reodering min qty is shop
        # is_shop standard_qty_shop_value
        warehouse_orderpoint_is_shop = self.product_id.orderpoint_ids.filtered(lambda a: a.location_id.is_shop == True)
        is_shop_list = warehouse_orderpoint_is_shop.mapped('id')
        standard_qty_shop_value = warehouse_orderpoint_is_shop.search([('id', 'in', is_shop_list)], limit=1,
                                                                      order='id desc')
        stock_quant_records = self.env['stock.quant'].search([('product_id', '=', self.product_id.id)])
        location_records = stock_quant_records.mapped('location_id')
        location_id = location_records.mapped('id')
        res = {}
        if location_id:
            res['domain'] = {'location_id': [('id', 'in', location_id), ('usage', '=', 'internal')]}

        self.last_request_date = last_return_request_record.min_date
        self.last_request_qty = product_qty
        self.stock_display_toko = standard_qty_shop_value.product_min_qty
        self.stock_current_toko = self.product_id.qty_available
        self.product_qty = 0.0
        self.product_uom_id = self.product_id.uom_id.id
        return res
