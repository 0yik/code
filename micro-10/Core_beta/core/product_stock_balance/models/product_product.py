# -*- coding: utf-8 -*-

from odoo import api, models


class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _get_domain_locations(self):
        """
        Overwrite core method to add check of user's default warehouse.
        """
        def_warehouse = self.env.user.default_warehouse
        if not (self._context.get('warehouse', False) or self._context.get('location', False)) \
                and def_warehouse:
            res = super(product_product, self.with_context(warehouse=def_warehouse.id))._get_domain_locations()
        else:
            res = super(product_product, self)._get_domain_locations()
        return res
