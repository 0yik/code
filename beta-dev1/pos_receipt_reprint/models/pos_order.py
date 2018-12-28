# -*- coding: utf-8 -*-

from odoo import models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    is_printed = fields.Boolean(string="printed")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

