from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    amount_service = fields.Float(compute='_compute_amount_all', string='Service Charge', digits=0, store=True)
    amount_tax = fields.Float(compute='_compute_amount_all', string='Taxes', digits=0, store=True)

    def compute_amount_all_wrapper(self):
        self._compute_amount_all()
        return True
