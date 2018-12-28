from openerp import fields, api, models
import logging

_logger = logging.getLogger(__name__)


class posOrder(models.Model):
    _inherit = "pos.order"

    picking_ids = fields.One2many('stock.picking', 'pos_order_id', 'Delivery Orders')

    @api.model
    def create_from_ui(self, orders):
        _logger.info('begin create_from_ui')
        combo_items = []
        for o in orders:
            if o['data'] and o['data'].has_key('lines'):
                for line in o['data']['lines']:
                    if line[2] and line[2].has_key('combo_items'):
                        print line[2]['combo_items']
                        for item in line[2]['combo_items']:
                            combo_items.append(item)
                        del line[2]['combo_items']
        order_ids = super(posOrder, self).create_from_ui(orders)
        sessions = self.env['pos.session'].search([('user_id', '=', self.env.user.id), ('state', '=', 'opened')])
        orders = self.browse(order_ids)
        if sessions:
            config = sessions[0].config_id
            customer_location = self.env.ref('stock.stock_location_customers')
            if config.auto_create_delivery_order and customer_location:
                for order in orders:
                    if (order.partner_id):
                        picking_out = self.env['stock.picking'].sudo().create({
                            'partner_id': order.partner_id.id,
                            'picking_type_id': self.env.ref('stock.picking_type_out').id,
                            'location_id': config.stock_location_id.id,
                            'location_dest_id': customer_location.id,
                            'pos_order_id': order.id
                        })
                        line_by_product_id = {}
                        for line in order.lines:
                            if line.product_id.is_combo == False:
                                if not line_by_product_id.has_key(line.product_id.id):
                                    line_by_product_id[line.product_id.id] = {
                                        'name': line.product_id.name,
                                        'product_id': line.product_id.id,
                                        'product_uom_qty': line.qty,
                                        'product_uom': line.product_id.uom_id.id,
                                        'picking_id': picking_out.id,
                                        'location_id': config.stock_location_id.id,
                                        'location_dest_id': customer_location.id,
                                    }
                                else:
                                    line_by_product_id[line.product_id.id]['product_uom_qty'] += line.qty
                        for combo_item in combo_items:
                            if not line_by_product_id.has_key(combo_item['product_id'][0]):
                                product = self.env['product.product'].browse(combo_item['product_id'][0])
                                line_by_product_id[combo_item['product_id'][0]] = {
                                    'name': product.name,
                                    'product_id': product.id,
                                    'product_uom_qty': combo_item['quantity'],
                                    'product_uom': product.uom_id.id,
                                    'picking_id': picking_out.id,
                                    'location_id': config.stock_location_id.id,
                                    'location_dest_id': customer_location.id,
                                }
                            else:
                                line_by_product_id[combo_item['product_id'][0]]['product_uom_qty'] += combo_item['quantity']
                        for key, vals in line_by_product_id.iteritems():
                            self.env['stock.move'].sudo().create(vals)
                        if config.picking_state == 'action_confirm':
                            picking_out.action_confirm()
                        if config.picking_state == 'force_assign':
                            picking_out.action_confirm()
                            picking_out.force_assign()
                        if config.picking_state == 'do_transfer':
                            picking_out.do_transfer()
        _logger.info('end create_from_ui')
        return order_ids
