import odoo
import odoo.modules.registry
import ast

from odoo import http, _
from odoo.http import request

import datetime
import json
import pytz
import os
import logging
import json

_logger = logging.getLogger(__name__)


class product_price_range(http.Controller):
    @http.route(['/api/product_range'], auth='public', csrf=False)
    def get_range(self, **post):
        data = json.loads(post.items()[0][0])
        course_id = int(data['product_id'])
        product_id = request.env['product.template'].sudo().browse(course_id)
        res = []
        if product_id:
            vals = {}
            vals.update({
                'min_sale_price'   : product_id.min_sale_price,
                'max_sale_price' : product_id.max_sale_price,
                'order_line'     :int(data['order_line']),
            })
            res.append(vals)
        return json.dumps(res);