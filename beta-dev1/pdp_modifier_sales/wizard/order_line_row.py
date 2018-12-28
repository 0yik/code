from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
import cStringIO
import tempfile
import binascii
import xlrd

class OrderLineRows(models.TransientModel):
    _name = "sale.order.line.row"

    row = fields.Float('Rows Showing')

    @api.model
    def default_get(self, fields):
        res = super(OrderLineRows, self).default_get(fields)
        if 'active_id' in self._context:
            order_id = self.env['sale.order'].browse(self._context['active_id'])
            rows = len(order_id.order_line)
            res['row'] = rows
        return res