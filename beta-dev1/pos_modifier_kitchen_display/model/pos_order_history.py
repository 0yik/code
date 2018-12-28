from openerp import api, fields, models, _
import json

class pos_order_history(models.Model):
    _name = 'order.history'
    _description = 'Restaurant Order History'

    order_item_id = fields.Many2one('product.product', string='Order Item')
    waiter_user_id = fields.Many2one('res.users', string='User')
    table_no = fields.Char(string='Table No.')
    order_no = fields.Char(string='Order No.')
    order_status = fields.Selection([
	    ('pending', 'Pending'),
	    ('done', 'Done'),
	    ], string='Order Status')
    start_time = fields.Char(string='Start Time')
    end_time = fields.Char(string='End Time')
    duration = fields.Char(string='Duration')
    line_id = fields.Char()


    @api.model
    def manage_order_history(self, order_line, start_time, table_info):
        order_line = json.loads(order_line) 
        print "\n session session", order_line
        order_history_vals = {
            'order_item_id': order_line.get('product_id'),
            'waiter_user_id': order_line['session_info']['created']['user']['id'],
            'table_no': table_info, 
            'order_no': order_line.get('order_uid'),
            'order_status': 'pending',
            'start_time': start_time,
            'line_id':order_line.get('id')
        }
        result = self.env['order.history'].create(order_history_vals)
        print "\n order_history_valsorder_history_vals", result
        return True


    @api.model
    def update_orders(self, order_id, end_time):
        values = []
        res = self.env['order.history'].search([('line_id','=',int(order_id))])
        print "\n ressssssssssssssssss", end_time
        vals = {'order_status': 'done',
                'end_time': end_time,
                'duration': end_time,
               }
        res_browse = res.write(vals)        


        return True
