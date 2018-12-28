# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
# You should have received a copy of the License along with this program.
#################################################################################
from openerp import models, fields, api, _

class pos_order(models.Model):
    _inherit = "pos.order"

    def _order_fields(self,ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        res.update({
            'note': ui_order.get('order_note') or False
        })
        return res

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_order_note = fields.Boolean('Enable Order Note')
    enable_product_note = fields.Boolean('Enable Product / Line Note')

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    line_note = fields.Char('Comment', size=512)
