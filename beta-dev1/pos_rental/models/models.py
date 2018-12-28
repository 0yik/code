# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime,timedelta
from odoo.tools import email_re, float_is_zero
from odoo.exceptions import UserError, ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    advance_product_id = fields.Many2one('product.product', 'Advance Deposit Product', domain=[('type', '=', 'service'), ('available_in_pos', '=', True)])


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rent_price = fields.Float("Rent price")
    is_booking_product = fields.Boolean(string="Can be Rented", default=True)


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    @api.model
    def get_product_data(self, vals):
        res = []
        product = self.browse(int(vals['id']))
        if product.booking_lines:
            for line in product.booking_lines:
                val = {
                    'start': line.actual_start_date,
                    'title': 'Qty '+ str(line.product_qty) + ' Booked',
                    'product_qty': line.product_qty,
                }
                if line.end_date:
                    val['end'] = line.end_date
                res.append(val)

                if line.end_date != line.actual_end_date:
                    bst_date = datetime.strptime(line.end_date, "%Y-%m-%d").date() + timedelta(days=1)
                    buffer_val = {
                        'start': str(bst_date),
                        'title': 'Laundry',
                        'end': line.actual_end_date,
                    }
                    res.append(buffer_val)
        return res

    booking_lines = fields.One2many('booking.order.line', 'product_id', string='Booking Lines')
    laundry_buffer = fields.Selection([('1','1'), ('2','2'), ('3','3'), ('7','7')], string='Laundry Buffer', help="Days required for laundry after each Booking.")
    advance_deposit = fields.Float(string='Advance Deposit')


class Picking(models.Model):
    _inherit = "stock.picking"

    pos_order_id=fields.Many2one("pos.order", "POS Order")
    src_of_tra = fields.Selection([('none', ''), ('walkin', 'Walkin'), ('online', 'Online')], string="Source of Transaction", compute="_compute_src_of_tra", default='none')

    @api.depends('pos_order_id')
    def _compute_src_of_tra(self):
        for pick in self.filtered('pos_order_id'):
            if pick.pos_order_id.online_order:
                pick.src_of_tra = 'online'
            else:
                pick.src_of_tra = 'walkin'

class Move(models.Model):
    _inherit = "stock.move"
    
    src_of_tra = fields.Selection([('none', ''), ('walkin', 'Walkin'), ('online', 'Online')], string="Source of Transaction", related='picking_id.src_of_tra', default='none')
    
class PosOrder(models.Model):
    _inherit = "pos.order"

    booking_id = fields.Many2one("booking.order")
    start_date = fields.Date(related="booking_id.def_start_date")
    end_date = fields.Date(related="booking_id.def_end_date")
    is_return_order=fields.Boolean('Advance Return Order', copy=False)
    return_order_id=fields.Many2one('pos.order', 'Advance Return Order of', readonly=True, copy=False)
    return_status=fields.Selection([
            ('-', 'None'),
            ('Fully-Returned', 'Fully Returned'),
            ('Partially-Returned', 'Partially Returned'),
            ('Non-Returnable', 'Non-Returnable')],
            'Advance Return Status', readonly=True, copy=False, default='-')
    return_date=fields.Date("Return Date")
    collected=fields.Boolean('Collected', copy=False)
    returned=fields.Boolean('Returned', copy=False)
    laundry=fields.Boolean('With Laundry', copy=False)
    all_done=fields.Boolean('Available', copy=False)
    pos_picking_id=fields.One2many("stock.picking", "pos_order_id", "Related Pickings")
    order_status=fields.Selection([
            ('Order-Received', 'Order-Received'),
            ('Order-Collected', 'Order-Collected'),
            ('Order-Returned', 'Order-Returned'),
            ('Laundry', 'Laundry'),
            ('Available', 'Available')
            ],
            'Order Status', readonly=True, copy=False)
    online_order = fields.Boolean("Online Order?")
    mail_status = fields.Char()
    
    def get_payment_journals(self):
        for obj in self:
            res = ''
            for pay in obj.statement_ids:
                res+= pay.journal_id.name + ','
            obj.payment_journals = res[:-1]
            
    payment_journals = fields.Char('Payment Journal',compute='get_payment_journals')
    
    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['booking_id'] = ui_order.get('booking_id')
        return fields
    
    @api.multi
    def create_laundry_picking(self):
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Delivery Orders')],limit=1)
        pick_vals = {
            'partner_id':self.partner_id.id,
            'move_type':'direct',
            'picking_type_id':picking_type_id.id,
            'location_id':picking_type_id.default_location_src_id.id,
            'location_dest_id':self.partner_id.property_stock_supplier.id,
            'booking_order_id':self.booking_id.id,
            'pos_order_id':self.id,
        }
        picking = self.env['stock.picking'].create(pick_vals)
        for line in self.lines.filtered(lambda line:line.product_id.type != 'service'):
            move_vals = {
                'product_id':line.product_id.id,
                'product_uom':line.product_id.uom_id.id,
                'product_uom_qty':line.qty,
                'name':line.product_id.name,
                'date_expected':datetime.now(),
                'picking_id':picking.id,
                'location_id':picking.location_id.id,
                'location_dest_id':picking.location_dest_id.id,
            }
            move_id = self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.force_assign()
        for operation in picking.pack_operation_product_ids:
            operation.qty_done = operation.product_qty
        picking.do_new_transfer()
        return True

    @api.multi
    def create_laundry_return_picking(self):
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Receipts')],limit=1)
        pick_vals = {
            'partner_id':self.partner_id.id,
            'move_type':'direct',
            'picking_type_id':picking_type_id.id,
            'location_id':self.partner_id.property_stock_supplier.id,
            'location_dest_id':picking_type_id.default_location_dest_id.id,
            'booking_order_id':self.booking_id.id,
            'pos_order_id':self.id,
        }
        picking = self.env['stock.picking'].create(pick_vals)
        for line in self.lines.filtered(lambda line:line.product_id.type != 'service'):
            move_vals = {
                'product_id':line.product_id.id,
                'product_uom':line.product_id.uom_id.id,
                'product_uom_qty':line.qty,
                'name':line.product_id.name,
                'date_expected':datetime.now(),
                'picking_id':picking.id,
                'location_id':picking.location_id.id,
                'location_dest_id':picking.location_dest_id.id,
            }
            move_id = self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.force_assign()
        for operation in picking.pack_operation_product_ids:
            operation.qty_done = operation.product_qty
        picking.do_new_transfer()
        return True

    def create_return_advance_payment(self, price):
        prec_acc = self.env['decimal.precision'].precision_get('Account')
        for order in self:
            session = order.session_id
            if session.state == 'closing_control' or session.state == 'closed':
                order.session_id = self._get_valid_session(session).id
            journal_ids = order.statement_ids.mapped('journal_id')

            if not float_is_zero(price, prec_acc):
                cash_journal_id = session.cash_journal_id.id
                if not cash_journal_id:
                    cash_journal = self.env['account.journal'].search([
                        ('type', '=', 'cash'),
                        ('id', 'in', journal_ids.ids),
                    ], limit=1)
                    if not cash_journal:
                        cash_journal = [statement.journal_id for statement in session.statement_ids if statement.journal_id.type == 'cash']
                        if not cash_journal:
                            raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
                    cash_journal_id = cash_journal[0].id
                order.add_payment({
                    'amount': -price,
                    'payment_date': fields.Datetime.now(),
                    'payment_name': _('return'),
                    'journal': cash_journal_id,
                })
                order.return_status = 'Fully-Returned'
        return True

    @api.multi
    def perform_button_operation(self, operation):
        error = False
        message = ""
        StockPicking = self.env['stock.picking']

        for order in self:
            if operation == "collected":
                if order.collected:
                    error = True
                    message = "Order already collected."
                elif order.returned:
                    error = True
                    message = "Order is already returned by the Customer. Order cannot be collected."
                elif order.laundry:
                    error = True
                    message = "Order is with vendor for laundry. Order cannot be collected."
                elif order.all_done:
                    error = True
                    message = "All processes associated with this order are complete. Order cannot be collected."
                else:
                    order.booking_id.validate_booking()
                    Pickings = StockPicking.search([('booking_order_id', '=', order.booking_id.id)])
                    Pickings.write({'pos_order_id': order.id})
                    outPikcings = Pickings.filtered(lambda p: p.picking_type_id.code == 'outgoing')
                    for picking in outPikcings:
                        picking.action_confirm()
                        picking.force_assign()
                        picking.action_done()
                    order.write({'collected': True, 'order_status': 'Order-Collected'})
            elif operation == "returned":
                if not order.collected:
                    error = True
                    message = "Order is not collected by customer. Order cannot be returned"
                elif order.returned:
                    error = True
                    message = "Order is already returned by the Customer. Order cannot be returned."
                elif order.laundry:
                    error = True
                    message = "Order is with vendor for laundry. Order cannot be returned."
                elif order.all_done:
                    error = True
                    message = "All processes associated with this order are complete. Order cannot be returned."
                else:
                    inPickings = StockPicking.search([('booking_order_id', '=', order.booking_id.id)]).filtered(lambda p: p.picking_type_id.code == 'incoming')
                    for picking in inPickings:
                        picking.action_confirm()
                        picking.force_assign()
                        picking.action_done()
                    order.write({'returned': True, 'order_status': 'Order-Returned'})
            elif operation == "laundry":
                if not order.collected:
                    error = True
                    message = "Order is not collected by customer. Order cannot be sent to laundry."
                elif not order.returned:
                    error = True
                    message = "Order is not returned by the Customer. Order cannot be sent to laundry."
                elif order.laundry:
                    error = True
                    message = "Order is already with vendor for laundry. Order cannot be sent to laundry."
                elif order.all_done:
                    error = True
                    message = "All processes associated with this order are complete. Order cannot be sent to laundry."
                else:
                    order.create_laundry_picking()
                    order.write({'laundry': True, 'order_status':'Laundry'})
            elif operation=="available":
                if not order.collected:
                    error = True
                    message = "Order is not collected by customer. Products cannot be set Available."
                elif not order.returned:
                    error = True
                    message = "Order is not returned by the Customer. Products cannot be set Available."
                elif not order.laundry:
                    error = True
                    message = "Order is not sent for laundry. Products cannot be set Available."
                elif order.all_done:
                    error = True
                    message = "All processes associated with this order are complete. Products cannot be set Available."
                else:
                    order.create_laundry_return_picking()
                    order.write({'all_done': True, 'order_status':'Available'})
        return {
            'error': error,
            'message': message
        }
        
    @api.multi
    def action_pos_order_paid(self):
        if not self.test_paid():
            raise UserError(_("Order is not paid."))
        self.write({'state': 'paid'})
        if self.booking_id:
            return True
        return self.create_picking()


class BookingOrder(models.Model):
    _inherit = 'booking.order'

    @api.model
    def create_from_pos_ui(self, order):
        vals = {}
        dates = []
        product = self.env['product.product'].browse(order.get('product_id'))
        for date in order['dates']:
            dates.append(datetime.strptime(date[:19], "%Y-%m-%d %H:%M:%S").date())
        start_date = min(dates)
        end_date = max(dates)
        actual_start_date = start_date - timedelta(days=product.default_preparation_days)
        actual_end_date = end_date + timedelta(days=int(order.get('buffer_days', 0)))
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        # check product is already booked for ordered product
        lines = self.env['booking.order.line'].search([('product_id', '=', product.id), ('state', '!=', 'returned')])
        for line in lines:
            start_dt, end_dt = fields.Date.from_string(line.actual_start_date), fields.Date.from_string(line.actual_end_date)
            if start_dt <= actual_start_date <= end_dt:
                return
            if start_dt <= actual_end_date <= end_dt:
                return

        vals['booking_lines'] = [(0, 0, {
                    'product_id': product.id,
                    'product_qty': 1,
                    'start_date': start_date,
                    'end_date': end_date,
                    'actual_start_date': actual_start_date.strftime("%Y-%m-%d"),
                    'actual_end_date': actual_end_date.strftime("%Y-%m-%d"),
                })]

        if order.get('booking_id'):
            booking = self.browse(order['booking_id'][0])
            booking.write(vals)
        else:
            vals.update({
                'def_start_date': actual_start_date,
                'def_end_date': actual_end_date,
                'partner_id': order['partner_id'],
            })
            booking = self.create(vals)
        return [booking.id, booking.name, booking.def_start_date, booking.def_end_date]

    @api.model
    def remove_product_from_booking(self, order):
        booking_id = order.get('booking_id')
        booking = self.env['booking.order'].browse(booking_id)
        product = self.env['product.product'].browse(order.get('product_id'))
        booking_line = self.env['booking.order.line'].search([('product_id', '=', product.id), ('order_id', '=', booking_id)])
        product.booking_lines.filtered(lambda l: l.order_id.id == booking_id).unlink()
        booking_line.unlink()
        return True


class BookingOrderLine(models.Model):
    _inherit = 'booking.order.line'

    partner_id = fields.Many2one("res.partner", related='order_id.partner_id')
    product_qty = fields.Integer("Qty")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    nric_no = fields.Char('NRIC No')
    email = fields.Char(required=True)

    @api.onchange('email')
    def _onchange_email(self):
        if self.email and not email_re.match(self.email):
            raise UserError(_("Invalid Email Address"))

    @api.constrains('email')
    def _contrains_email(self):
        for partner in self:
            if partner.email and not email_re.match(partner.email):
                raise ValidationError(_("Invalid Email Address"))


class StockMove(models.Model):
    _inherit = 'stock.move'

    image_small = fields.Binary(related='product_id.image_small')
    attention = fields.Char()
    item = fields.Char()
    invoice_control = fields.Selection([('all', 'All')])
    dest_address = fields.Text("Destination Address")
    
class PosConfigSetting(models.TransientModel):
    _inherit = 'pos.config.settings'
    
    email_sub = fields.Char(string="Emal Subject")
    email_body = fields.Html(String="Email Body")
    
    @api.model
    def get_default_email_val(self, fields):
        email_sub = self.env.ref('account.email_template_edi_invoice').subject
        email_body = self.env.ref('account.email_template_edi_invoice').body_html
        return {'email_sub': email_sub,'email_body':email_body}

    @api.multi
    def set_default_email_val(self):
        for record in self:
            self.env.ref('account.email_template_edi_invoice').write({
            'subject': str(record.email_sub),
            'body_html':str(record.email_body),
            })


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_booked = fields.Boolean()
    is_ordered = fields.Boolean()
