from odoo import api, fields, models, _
import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit = 'sale.order'

    validity_date = fields.Date(readonly=True,compute='get_validity_date')
    category_id = fields.Many2one('product.group','Category',required=True)
    wh_location = fields.Char(string="Location")

    # Generating modified sequence for sale order
    @api.model
    def create(self, vals):
        group = vals.get('category_id')
        partobj = self.env['product.group'].browse(group).singkatan
        import datetime
        now = datetime.datetime.now()
        year_init = now.strftime('%y')
        code = self.env.user.company_id
        seq = self.env['ir.sequence'].next_by_code('sale.order')
        seq_num = seq.split("SO")[1]
        final_value = str('SO') + str(code.company_code) + str(partobj) + str(year_init) + str(seq_num)
        vals['name'] = final_value
        res = super(sale_order, self).create(vals)
        return res

    @api.model
    def get_validity_date(self):
        if self.date_order:
            validity_datetime = datetime.datetime.strptime(self.date_order,DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=4)
            self.validity_date = validity_datetime.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.onchange('date_order')
    def get_validity_date(self):
        if self.date_order:
            validity_datetime = datetime.datetime.strptime(self.date_order, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                days=4)
            self.validity_date = validity_datetime.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.onchange('category_id')
    def onchange_category_id(self):
        if self.category_id:
            if self.order_line:
                self.order_line = []

sale_order()

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    on_hand = fields.Integer(compute='_compute_on_hand', string='On Hand')

    def _compute_on_hand(self):
        total = 0
        for item in self:
            total += int(item.product_id.qty_available)
        self.on_hand = total



    product_id = fields.Many2one('product.product','Product',domain="[('product_tmpl_id.product_group','=',parent.category_id or '12345678')]")

sale_order_line()

class DeliveryPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning("-clear_program_fee_payment_vals-- %s.", self.env.context)
        code = self.env.user.company_id
        picking_type_obj = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
        warehouse_short_name = picking_type_obj.warehouse_id.code
        sale_obj = self.env['sale.order'].search([('name', '=', vals['origin'])])
        final_value = '/'
        if sale_obj and not self.env.context.get('from_so'):
            seq = self.env['ir.sequence'].search([('prefix','=','SOUT%(y)s')], limit=1)
            if seq:
                seq_name = seq._next()
            else:
                seq_name = self.env['ir.sequence'].next_by_code('stock.picking')
            final_value = str(warehouse_short_name) + str(code.company_code) + str(seq_name)
        elif not sale_obj and self.env.context.get('from_so'):
            seq = self.env['ir.sequence'].search([('prefix', '=', 'SIN%(y)s')], limit=1)
            if seq:
                seq_name = seq._next()
            else:
                seq_name = self.env['ir.sequence'].next_by_code('stock.picking')
            final_value = str(warehouse_short_name) + str(code.company_code) + str(seq_name)
        vals['name'] = final_value
        return super(DeliveryPicking, self).create(vals)

DeliveryPicking()





