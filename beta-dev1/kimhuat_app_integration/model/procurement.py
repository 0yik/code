# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class Product(models.Model):
    _inherit = 'product.product'

    @api.onchange('is_equipment')
    def onchage_is_equipment(self):
        """docstring for onchage_is_equipment"""
        if self.is_equipment:
            self.type = 'product'

    @api.multi
    def _need_procurement(self):
        for product in self:
            if product.type not in ['digital']:
                return True
        return super(Product, self)._need_procurement()


Product()

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    @api.returns('procurement.rule', lambda value: value.id if value else False)
    def _find_suitable_rule(self):
        rule = super(ProcurementOrder, self)._find_suitable_rule()
        Pull = self.env['procurement.rule']
        if not rule:
            rule = Pull.search([], limit=1)
        return rule

    @api.multi
    def _assign(self):
        '''This method check what to do with the given procurement in order to complete its needs.
        It returns False if no solution is found, otherwise it stores the matching rule (if any) and
        returns True.
        :rtype: boolean
        '''
        # if the procurement already has a rule assigned, we keep it (it has a higher priority as it may have been chosen manually)
        if self.rule_id:
            return True
        elif self.product_id.type not in ('digital', 'service'):
            rule = self._find_suitable_rule()
            if rule:
                self.write({'rule_id': rule.id})
                return True
        elif self.product_id.type in ('service') and self.sale_line_id.order_id:
            rule = self._find_suitable_rule()
            if rule:
                self.write({'rule_id': rule.id})
                return True
        return False


ProcurementOrder()

