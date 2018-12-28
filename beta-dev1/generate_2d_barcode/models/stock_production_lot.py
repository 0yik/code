# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re

class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    def get_barcode(self):
        data = self.product_id.barcode + ',' + self.name + ','
        if self.use_date:
            data += self.use_date
        return re.escape(data)

stock_production_lot()