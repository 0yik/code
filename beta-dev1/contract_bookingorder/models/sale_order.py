# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    analytic_line_id = fields.Many2one(
        comodel_name='bo.account.analytic.line',
        string='Bo analytic Line Ref.', help='Technical field to view BO.')


SaleOrder()
