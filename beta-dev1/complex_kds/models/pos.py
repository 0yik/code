from odoo import api, fields, models, _
import json
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from functools import partial

class pos_config(models.Model):
    _inherit = "pos.config"

    screen_type = fields.Selection(selection_add=[
        ('kitchen', 'KDS'),
        ('summary', 'Summary'),
    ],  string='Session Type', default='waiter')

    category_mapping_lines = fields.One2many('category.mapping.line', 'config_id',)
    category_summery_lines = fields.One2many('category.mapping.line', 'config_id2',)

    @api.multi
    @api.constrains('category_mapping_lines', 'category_summery_lines')
    def _check_reconcile(self):
        for config in self:
            kitchen_categ = []
            summary_categ = []
            for categ in self.category_mapping_lines:
                if set(categ.categ_ids.ids).intersection(kitchen_categ):
                    raise ValidationError(_('You can not repeat category in kitchen screens'))
                if categ.next_pos_config_id.branch_id != config.branch_id:
                    raise ValidationError(_('Branch Must be same of Kitchen and waiter'))
                if categ.next_pos_config_id.bus_id != config.bus_id:
                    raise ValidationError(_('Bus Must be same of Kitchen and waiter'))
                kitchen_categ.extend(categ.categ_ids.ids)
            for categ in self.category_summery_lines:
                if set(categ.categ_ids.ids).intersection(summary_categ):
                    raise ValidationError(_('You can not repeat category in summary screens'))
                if categ.next_pos_config_id.branch_id != config.branch_id:
                    raise ValidationError(_('Branch Must be same of Kitchen and waiter'))
                if categ.next_pos_config_id.bus_id != config.bus_id:
                    raise ValidationError(_('Bus Must be same of Kitchen and waiter'))
                summary_categ.extend(categ.categ_ids.ids)

class sales_order(models.Model):
    _inherit = 'sale.order'

    pos_order_ref = fields.Char('Pos Order')
    session_id = fields.Many2one('pos.session', string="POS Session")

class PosSalesOrder(models.Model):
    _inherit = "pos.sales.order"

    @api.model
    def create_pos_sale_order(self, ui_order, note, cashier, client_fields, exp_date):
        order_data = super(PosSalesOrder, self).create_pos_sale_order(ui_order, note, cashier, client_fields, exp_date)
        order = self.env['sale.order'].search([('id', '=', order_data.get('id'))])
        #order.client_order_ref = ui_order.get('uid') or 'Point of sale'
        order.pos_order_ref = ui_order.get('uid') or 'Point of sale'
        print "=============ui_order.get('session_id',False)===========",ui_order
        order.session_id = ui_order.get('pos_session_id',False)
        return order_data

    @api.model
    def confirm_sale(self, order_uid):
        orders = self.env['sale.order'].search([('pos_order_ref', '=', order_uid)])
        for order in orders.filtered(lambda o:o.state in ['draft', 'sent']):
            order.action_confirm()
        return True

class CategoryMappingLine(models.Model):
    _name = 'category.mapping.line'

    categ_ids= fields.Many2many('pos.category', string="Categories")
    next_pos_config_id = fields.Many2one('pos.config')
    ip_address = fields.Char('IP Address')
    config_id = fields.Many2one('pos.config')
    config_id2 = fields.Many2one('pos.config')

class pos_order_history(models.Model):
    _name = 'order.history'
    _description = 'Restaurant Order History'

    order_item_id = fields.Many2one('product.product', string='Order Item')
    waiter_user_id = fields.Many2one('res.users', string='User')
    table_id = fields.Many2one('restaurant.table',string='Table No.')
    order_no = fields.Char(string='Order No.')
    order_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
        ], string='Order Status')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    duration = fields.Integer(string='Duration in seconds')
    line_id = fields.Char('Line ')
    current_screen = fields.Many2one('pos.config', 'Current Screen')
    screen_name = fields.Char('Screen Name')
    order_id = fields.Many2one('pos.order', 'Order')
    history_type = fields.Selection([('order', 'Order'), ('orderline', 'Order Line')])
    orderline_id = fields.Many2one('pos.order.line', 'OrderLine')

    @api.model
    def manage_order_line_history(self, order_line, start_time, table_id, current_screen, screen_name):
        order_line = json.loads(order_line) 
        history = self.search([('line_id', '=', order_line.get('uid')),
        ('order_no', '=', order_line.get('order_uid')),
        ('current_screen', '=', current_screen),])
        print "OrderLine    ",order_line
        order_history_vals = {
            'order_item_id': order_line.get('product_id'),
            'waiter_user_id': order_line.get('session_info') and order_line['session_info']['created']['user']['id'] or False,
            'table_id': table_id, 
            'order_no': order_line.get('order_uid'),
            'order_status': 'pending',
            'start_time': start_time,
            'line_id':order_line.get('uid'),
            'current_screen': current_screen,
            'screen_name': screen_name,
            'history_type': 'orderline',
        }
        if not history:
            result = self.create(order_history_vals)
        return True

    @api.model
    def manage_order_history(self, order, start_time, table_id, current_screen, screen_name, duration, end_time):
        order = json.loads(order) 
        history = self.search([('order_no', '=', order.get('uid')),
        ('current_screen', '=', current_screen),
        ('table_id', '=', table_id), 
        ('order_status', '=', 'pending'),
        ('history_type', '=', 'order')])
        order_history_vals = {
            # 'order_item_id': order_line.get('product_id'),
            'waiter_user_id': '',
            'table_id': table_id, 
            'order_no': order.get('uid'),
            'order_status': 'done',
            'start_time': start_time,
            # 'line_id':order_line.get('id'),
            'current_screen': current_screen,
            'end_time': end_time,
            'duration': duration,
            'history_type': 'order',
        }
        order = self.env['pos.order'].search([('pos_reference', 'like', order.get('uid'))])
        if order:
            order_history_vals['order_id'] = order.id
        if not history:
            result = self.create(order_history_vals)
        return True

    @api.model
    def update_orders(self, order_uid ,line_uid, duration, end_time, current_screen):
        values = []
        res = self.env['order.history'].search([('order_no', '=', order_uid),('line_id','=',line_uid), ('current_screen', '=', current_screen)])
        vals = {'order_status': 'done',
                'end_time': end_time,
                'duration': duration,
               }
        order = self.env['pos.order'].search([('pos_reference', 'like', order_uid)])
        if order:
            vals['order_id'] = order.id

        order_line = self.env['pos.order.line'].search([('order_id.pos_reference', 'like', order_uid), ('uid', '=', line_uid)])
        if order_line:
            vals['orderline_id'] = order_line.id
        res_browse = res.write(vals)        
        return True

    @api.model
    def get_history(self, current_screen):
        values = []
        domain = []
        if current_screen:
            domain = [('current_screen', '=', current_screen)]
        order_history = self.sudo().search(domain)
        for record in order_history:
            values.append({ 'id': record.id,
                            'product': record.order_item_id.name,
                            'user':record.waiter_user_id.name,
                            'table': record.table_id.name,
                            'order':record.order_no,
                            'status':record.order_status,
                            'start':record.start_time,
                            'end':record.end_time,
                            'duration':record.duration
                        })
        return values

class Product(models.Model):
    _inherit = 'product.template'

    normal_time_cook = fields.Integer('Normal Time to cook(In seconds)')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    payment_date = fields.Datetime('Payment Date')
    cancelled_lines = fields.One2many('pos.order.line', 'order_id2')

    @api.model
    def _process_order(self, pos_order):
        order = super(PosOrder, self)._process_order(pos_order)
        order_history = self.env['order.history'].search([('order_no', '=', pos_order['uid']), ('history_type', '=', 'order')], limit=1)
        if order_history:
            order_history.order_id = order.id
        for line in order.lines:
            order_histories = self.env['order.history'].search([('order_no', '=', pos_order['uid']), ('history_type', '=', 'orderline'), ('line_id', '=', line.uid)])
            for order_history in order_histories:
                order_history.orderline_id = line.id
        order.payment_date = datetime.now()
        return order

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        process_line = partial(self.env['pos.order.line']._order_line_fields)
        res['cancelled_lines'] = [process_line(l) for l in ui_order['cancelled_lines']] if ui_order['cancelled_lines'] else []
        for l in res['cancelled_lines']:
            l[2]['active'] = False
            res['lines'].append(l)
        return res

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    uid = fields.Char('UID')
    order_id2 = fields.Many2one('pos.order',string='Cancelled Lines')
    active = fields.Boolean('Active', default=True)
    cancel_manager = fields.Many2one('res.users', 'Manager')

class ResUsers(models.Model):
    _inherit = 'res.users'

    pin_number = fields.Integer(string="PIN Number")

    _sql_constraints = [
        ('unique_pin', 'unique (pin_number)', 'The PIN NUmber must be unique!')
    ]
    
    @api.model
    def compare_pin_number_get_manager(self, pin_number):
        group_pos_manager_id = self.env.ref('point_of_sale.group_pos_manager')
        print "group_pos_manager_id     ",group_pos_manager_id,type(pin_number)
        manager = self.search([('groups_id', 'in', group_pos_manager_id.id), ('pin_number', '=', int(pin_number))], limit=1)
        print "USER IDSSSS   ",pin_number
        print ">>>>>>>>>>>>>>>>>>>>   ",manager,manager.id,manager.name
        if manager:
            return manager[0].id
        return False